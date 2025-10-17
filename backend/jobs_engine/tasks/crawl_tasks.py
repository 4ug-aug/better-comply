"""Celery tasks for the crawl pipeline stage."""

from __future__ import annotations

import hashlib
import logging
import traceback
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

import requests

from jobs_engine.tasks.common import simple_task
from jobs_engine.minio_client import MinIOClient
from models.artifact import Artifact
from models.subscription import Subscription
from models.source import Source
from models.run import Run
from events.kafka_emitter import emit_event
from events.run_status_emitter import (
    emit_run_started,
    emit_run_completed,
    emit_run_failed,
)
from database.sync import SessionLocalSync

logger = logging.getLogger(__name__)


@simple_task(
    name="jobs_engine.tasks.crawl_tasks.handle_subscription_scheduled",
    queue="jobs",
    job_type="subs.schedule"
)
def handle_subscription_scheduled(
    subscription_id: int,
    run_id: int,
    trace_id: str = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Handle a scheduled subscription event.
    
    When a subscription is due to run, this task:
    1. Fetches the subscription and source details
    2. Generates a crawl request ID
    3. Emits a crawl.request event for the source base URL
    
    This is the first stage of the pipeline. The run stays RUNNING
    until the final delivery stage completes.
    
    Args:
        subscription_id: The subscription ID that is due to run
        run_id: The run ID created for this execution
        trace_id: Trace ID for provenance tracking (generated if not provided)
        **kwargs: Additional keyword arguments (job_id, etc.)
        
    Returns:
        Dictionary with task status and emitted event details
    """
    if not trace_id:
        trace_id = str(uuid4())
    
    logger.info(
        f"Handling subscription scheduled: sub_id={subscription_id}, "
        f"run_id={run_id}, trace_id={trace_id}"
    )
    
    # Emit run.started event - begins the pipeline
    emit_run_started(run_id, trace_id)
    
    try:
        with SessionLocalSync() as db:
            # Fetch subscription and source
            subscription = db.get(Subscription, subscription_id)
            if not subscription:
                raise ValueError(f"Subscription {subscription_id} not found")
            
            source = db.get(Source, subscription.source_id)
            if not source:
                raise ValueError(f"Source {subscription.source_id} not found")
            
            run = db.get(Run, run_id)
            if not run:
                raise ValueError(f"Run {run_id} not found")
            
            # Generate a unique crawl request ID
            crawl_request_id = str(uuid4())
            
            # Emit crawl.request event for the source base URL
            payload = {
                "url": source.base_url,
                "source_id": source.id,
                "run_id": run_id,
                "crawl_request_id": crawl_request_id,
                "trace_id": trace_id,
                "subscription_id": subscription_id,
            }
            
            emit_event("crawl.request", payload, topic="crawl.request")
            
            logger.info(
                f"Emitted crawl.request: url={source.base_url}, "
                f"crawl_request_id={crawl_request_id}"
            )
            
            return {
                "status": "success",
                "crawl_request_id": crawl_request_id,
                "trace_id": trace_id,
                "url": source.base_url,
            }
    
    except Exception as e:
        logger.exception(f"Error handling subscription scheduled: {e}")
        # Emit run.failed event - halts the pipeline
        emit_run_failed(run_id, trace_id, str(e), traceback.format_exc())
        raise


@simple_task(
    name="jobs_engine.tasks.crawl_tasks.crawl_url",
    queue="jobs",
    job_type="crawl.url"
)
def crawl_url(
    url: str,
    source_id: int,
    run_id: int,
    crawl_request_id: str,
    trace_id: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Crawl a URL and store the raw content in MinIO.
    
    This is an intermediate stage of the pipeline. The run stays RUNNING
    until the final delivery stage completes.
    
    Args:
        url: The URL to crawl
        source_id: The source ID
        run_id: The run ID
        crawl_request_id: Unique ID for this crawl request
        trace_id: Trace ID for provenance tracking
        **kwargs: Additional keyword arguments
        
    Returns:
        Dictionary with crawl result details including artifact_id and blob_uri
    """
    logger.info(f"Crawling URL: {url} (crawl_request_id={crawl_request_id})")
    
    # Emit run.started event if not already marked as running
    # (First time we execute for this run)
    emit_run_started(run_id, trace_id)
    
    try:
        with SessionLocalSync() as db:
            # Fetch the source to get auth/rate limit config
            source = db.get(Source, source_id)
            if not source:
                raise ValueError(f"Source {source_id} not found")
            
            # Fetch the URL
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            content = response.content
            content_type = response.headers.get("content-type", "application/octet-stream")
            status_code = response.status_code
            
            # Compute SHA256 hash of content
            content_hash = hashlib.sha256(content).hexdigest()
            
            # Upload to MinIO
            minio = MinIOClient()
            
            # Create path: raw/{source_id}/{yyyy}/{mm}/{dd}/{sha256}.bin
            now = datetime.utcnow()
            object_key = (
                f"raw/{source_id}/{now.year:04d}/{now.month:02d}/{now.day:02d}/"
                f"{content_hash}.bin"
            )
            
            success = minio.upload_artifact(
                bucket_name="artifacts",
                object_key=object_key,
                data=content,
                content_type=content_type,
            )
            
            if not success:
                raise ValueError("Failed to upload artifact to MinIO")
            
            blob_uri = f"s3://artifacts/{object_key}"
            logger.info(f"Uploaded to MinIO: {blob_uri}")
            
            # Create Artifact record
            artifact = Artifact(
                source_url=url,
                content_type=content_type,
                blob_uri=blob_uri,
                fetch_hash=content_hash,
                run_id=run_id,
            )
            db.add(artifact)
            db.flush()
            
            artifact_id = artifact.id
            db.commit()
            
            # Emit crawl.result event - triggers next pipeline stage
            result_payload = {
                "artifact_id": artifact_id,
                "blob_uri": blob_uri,
                "content_type": content_type,
                "status_code": status_code,
                "headers": dict(response.headers),
                "run_id": run_id,
                "trace_id": trace_id,
                "source_url": url,
            }
            
            emit_event("crawl.result", result_payload, topic="crawl.result")
            
            logger.info(
                f"Successfully crawled and stored: artifact_id={artifact_id}, "
                f"hash={content_hash}"
            )
            
            return result_payload
    
    except Exception as e:
        logger.exception(f"Error crawling URL {url}: {e}")
        # Emit run.failed event - halts the pipeline
        # Don't emit crawl.result on failure - pipeline stops
        emit_run_failed(run_id, trace_id, str(e), traceback.format_exc())
        raise


@simple_task(
    name="jobs_engine.tasks.crawl_tasks.parse_crawled_content",
    queue="jobs",
    job_type="parse.content"
)
def parse_crawled_content(
    artifact_id: int,
    blob_uri: str,
    run_id: int,
    trace_id: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Parse crawled content. Placeholder for future implementation.
    
    This task will be triggered by parse.request events and will:
    - Download artifact from MinIO
    - Extract structured content and text
    - Store parsed result
    - Emit parse.result event
    
    Args:
        artifact_id: ID of the artifact to parse
        blob_uri: MinIO URI of the artifact
        run_id: The run ID
        trace_id: Trace ID for provenance tracking
        **kwargs: Additional keyword arguments
        
    Raises:
        NotImplementedError: This phase is not yet implemented
    """
    logger.info(
        f"parse_crawled_content called: artifact_id={artifact_id}, "
        f"blob_uri={blob_uri}"
    )
    try:
        raise NotImplementedError(
            "Parse phase not yet implemented. Listening to parse.request events."
        )
    except Exception as e:
        logger.exception(f"Error parsing crawled content: {e}")
        # Emit run.failed event - halts the pipeline
        emit_run_failed(run_id, trace_id, str(e), traceback.format_exc())
        raise


@simple_task(
    name="jobs_engine.tasks.crawl_tasks.version_document",
    queue="jobs",
    job_type="version.document"
)
def version_document(
    parse_result_id: int,
    run_id: int,
    trace_id: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Version a parsed document. Placeholder for future implementation.
    
    This task will be triggered by versioning.request events and will:
    - Compare with previous version
    - Compute diffs
    - Store new version metadata
    - Emit versioning.result event
    
    Args:
        parse_result_id: ID of the parse result
        run_id: The run ID
        trace_id: Trace ID for provenance tracking
        **kwargs: Additional keyword arguments
        
    Raises:
        NotImplementedError: This phase is not yet implemented
    """
    logger.info(
        f"version_document called: parse_result_id={parse_result_id}"
    )
    raise NotImplementedError(
        "Versioning phase not yet implemented. Listening to versioning.request events."
    )


@simple_task(
    name="jobs_engine.tasks.crawl_tasks.deliver_document",
    queue="jobs",
    job_type="deliver.document"
)
def deliver_document(
    version_id: int,
    run_id: int,
    trace_id: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Deliver a versioned document. Placeholder for future implementation.
    
    This is the FINAL stage of the pipeline. This task should:
    - Send to downstream systems
    - Emit delivery notifications
    - Emit run.completed event (mark run as COMPLETED since this is the final stage)
    
    Args:
        version_id: ID of the version to deliver
        run_id: The run ID
        trace_id: Trace ID for provenance tracking
        **kwargs: Additional keyword arguments
        
    Raises:
        NotImplementedError: This phase is not yet implemented
    """
    logger.info(
        f"deliver_document called: version_id={version_id}"
    )
    raise NotImplementedError(
        "Delivery phase not yet implemented. Listening to delivery.request events. "
        "When implemented, remember to emit run.completed(run_id, trace_id) "
        "since this is the final pipeline stage."
    )

"""Celery tasks for the crawl pipeline stage."""

from __future__ import annotations

import hashlib
import logging
import traceback
from datetime import datetime, timezone
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
    emit_run_failed,
    emit_run_completed,
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
            now = datetime.now(timezone.utc)
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
                "source_id": source_id,
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
    source_url: str = None,
    source_id: int = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Parse crawled HTML content and extract structured sections.
    
    This is an intermediate stage of the pipeline. The run stays RUNNING
    until the final delivery stage completes.
    
    Args:
        artifact_id: ID of the artifact to parse
        blob_uri: MinIO URI of the artifact (s3://artifacts/raw/...)
        run_id: The run ID
        trace_id: Trace ID for provenance tracking
        source_url: Source URL for the artifact
        **kwargs: Additional keyword arguments
        
    Returns:
        Dictionary with parse result including doc_id and version_id
    """
    logger.info(
        f"Parsing HTML artifact: artifact_id={artifact_id}, "
        f"source_url={source_url}, blob_uri={blob_uri}"
    )
    
    # Emit run.started if not already marked as running
    emit_run_started(run_id, trace_id)
    
    try:
        from jobs_engine.utils.minio_artifact_handler import (
            download_artifact,
            upload_parsed_document,
            upload_raw_metadata,
        )
        from jobs_engine.utils.html_parser import (
            detect_encoding,
            parse_html_to_sections,
        )
        from models.document import Document
        from models.document_version import DocumentVersion

        # Download artifact from MinIO
        logger.info(f"Downloading artifact from {blob_uri}")
        content_bytes = download_artifact(blob_uri)

        # Detect encoding
        encoding, encoding_method, confidence = detect_encoding({}, content_bytes)
        html_text = content_bytes.decode(encoding, errors="replace")

        logger.info(
            f"Decoded artifact with {encoding} (method: {encoding_method}, "
            f"confidence: {confidence})"
        )

        # Parse HTML to sections
        parsed_doc = parse_html_to_sections(html_text, source_url, content_bytes)

        # Create or get Document
        with SessionLocalSync() as db:
            # Get or create document
            doc = db.query(Document).filter_by(source_url=source_url).first()
            if not doc:
                doc = Document(
                    source_id=source_id,
                    source_url=source_url,
                    published_date=parsed_doc.published_date,
                    language=parsed_doc.language,
                )
                db.add(doc)
                db.flush()
                logger.info(f"Created new Document: id={doc.id}, url={source_url}")
            else:
                logger.info(f"Using existing Document: id={doc.id}")

            # Create DocumentVersion
            import hashlib
            import json

            parsed_dict = parsed_doc.model_dump()
            parsed_json = json.dumps(parsed_dict, sort_keys=True)
            content_hash = hashlib.sha256(parsed_json.encode()).hexdigest()

            version = DocumentVersion(
                document_id=doc.id,
                content_hash=content_hash,
                run_id=run_id,
                parsed_uri="",  # Will be updated after upload
                diff_uri=None,
            )
            db.add(version)
            db.flush()
            version_id = version.id

            logger.info(f"Created DocumentVersion: id={version_id}")

            db.commit()

        # Upload parsed document to MinIO
        parsed_uri = upload_parsed_document(doc.id, version_id, parsed_dict)

        # Upload raw metadata
        raw_metadata = {
            "artifact_id": artifact_id,
            "source_url": source_url,
            "fetch_timestamp": parsed_doc.fetch_timestamp,
            "encoding": encoding,
            "encoding_method": encoding_method,
            "encoding_confidence": confidence,
            "content_length": len(content_bytes),
        }
        upload_raw_metadata(content_hash, raw_metadata)

        # Update DocumentVersion with parsed_uri
        with SessionLocalSync() as db:
            version = db.get(DocumentVersion, version_id)
            if version:
                version.parsed_uri = parsed_uri
                db.commit()

        # Emit parse.result event
        result_payload = {
            "doc_id": doc.id,
            "version_id": version_id,
            "parsed_uri": parsed_uri,
            "section_count": len(parsed_doc.sections),
            "run_id": run_id,
            "trace_id": trace_id,
            "source_url": source_url,
        }

        emit_event("parse.result", result_payload, topic="parse.result")

        logger.info(
            f"Successfully parsed HTML: doc_id={doc.id}, "
            f"sections={len(parsed_doc.sections)}"
        )

        return result_payload

    except Exception as e:
        logger.exception(f"Error parsing HTML artifact {artifact_id}: {e}")
        # Emit run.failed event - halts the pipeline
        emit_run_failed(run_id, trace_id, str(e), traceback.format_exc())
        raise


@simple_task(
    name="jobs_engine.tasks.crawl_tasks.version_document",
    queue="jobs",
    job_type="version.document"
)
def version_document(
    doc_id: int,
    version_id: int,
    parsed_uri: str,
    run_id: int,
    trace_id: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Version a parsed document by computing diffs against previous version.
    
    This is an intermediate stage of the pipeline. Runs stay RUNNING until
    the final delivery stage completes.
    
    This task:
    - Fetches the current and previous document versions
    - Computes JSON Patch RFC 6902 diff (or sets diff_uri=NULL for first version)
    - Stores diff to MinIO if applicable
    - Emits versioning.result event
    
    Args:
        doc_id: ID of the document
        version_id: ID of the document version
        parsed_uri: URI to the parsed content in MinIO
        run_id: The run ID
        trace_id: Trace ID for provenance tracking
        **kwargs: Additional keyword arguments
        
    Returns:
        Dictionary with versioning result
    """
    logger.info(
        f"version_document: doc_id={doc_id}, version_id={version_id}, parsed_uri={parsed_uri}"
    )
    
    # Emit run.started if not already marked as running
    emit_run_started(run_id, trace_id)
    
    try:
        import json
        from jobs_engine.utils.minio_artifact_handler import download_artifact
        from jobs_engine.utils.diff_generator import compute_json_patch_diff
        from models.document_version import DocumentVersion

        # Load current (new) parsed document from MinIO
        logger.info(f"Loading parsed document from {parsed_uri}")
        parsed_json_bytes = download_artifact(parsed_uri)
        new_parsed_doc = json.loads(parsed_json_bytes.decode('utf-8'))

        diff_uri = None

        # Query for previous version (ordered by created_at DESC, skip current)
        with SessionLocalSync() as db:
            previous_version = (
                db.query(DocumentVersion)
                .filter(DocumentVersion.document_id == doc_id)
                .filter(DocumentVersion.id != version_id)  # Exclude current
                .order_by(DocumentVersion.created_at.desc())
                .first()
            )

            if previous_version:
                logger.info(
                    f"Found previous version: id={previous_version.id}, "
                    f"uri={previous_version.parsed_uri}"
                )

                # Load old parsed document
                old_parsed_json_bytes = download_artifact(previous_version.parsed_uri)
                old_parsed_doc = json.loads(old_parsed_json_bytes.decode('utf-8'))

                # Compute JSON Patch RFC 6902 diff
                patch_operations = compute_json_patch_diff(old_parsed_doc, new_parsed_doc)

                if patch_operations:
                    logger.info(
                        f"Computed {len(patch_operations)} patch operations for "
                        f"version {version_id}"
                    )

                    # Upload diff to MinIO
                    object_key = f"diffs/{doc_id}/{version_id}.json"
                    diff_data = json.dumps(patch_operations, indent=2).encode('utf-8')
                    
                    from io import BytesIO
                    from jobs_engine.minio_client import MinIOClient

                    minio = MinIOClient()
                    data_stream = BytesIO(diff_data)
                    minio.client.put_object(
                        bucket_name="artifacts",
                        object_name=object_key,
                        data=data_stream,
                        length=len(diff_data),
                        content_type="application/json",
                    )

                    diff_uri = f"s3://artifacts/{object_key}"
                    logger.info(f"Uploaded diff to {diff_uri}")

                    # Update DocumentVersion with diff_uri
                    with SessionLocalSync() as db:
                        current_version = db.get(DocumentVersion, version_id)
                        if current_version:
                            current_version.diff_uri = diff_uri
                            db.commit()
                else:
                    logger.info("No previous version found - this is the first version")
                    # diff_uri stays NULL for first version
                    pass

        # Emit versioning.result event
        result_payload = {
            "doc_id": doc_id,
            "version_id": version_id,
            "diff_uri": diff_uri,
            "run_id": run_id,
            "trace_id": trace_id,
        }

        emit_event("versioning.result", result_payload, topic="versioning.result")

        logger.info(
            f"Successfully versioned document: doc_id={doc_id}, "
            f"version_id={version_id}, diff_uri={diff_uri}"
        )

        return result_payload

    except Exception as e:
        logger.exception(f"Error versioning document {doc_id}: {e}")
        # Emit run.failed event - halts the pipeline
        emit_run_failed(run_id, trace_id, str(e), traceback.format_exc())
        raise


@simple_task(
    name="jobs_engine.tasks.crawl_tasks.deliver_document",
    queue="jobs",
    job_type="deliver.document"
)
def deliver_document(
    doc_id: int,
    version_id: int,
    run_id: int,
    trace_id: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Deliver a versioned document to downstream systems.
    
    This is the FINAL stage of the pipeline. After this stage completes,
    the entire run transitions to COMPLETED status.
    
    This task:
    - Fetches the DocumentVersion and loads parsed content from MinIO
    - Creates a DeliveryEvent record to track the delivery
    - Emits delivery.request event for downstream systems to consume
    - Emits delivery.result event to complete the pipeline
    - Updates DeliveryEvent status to COMPLETED
    
    Args:
        doc_id: ID of the document
        version_id: ID of the version to deliver
        run_id: The run ID
        trace_id: Trace ID for provenance tracking
        **kwargs: Additional keyword arguments
        
    Returns:
        Dictionary with delivery result
    """
    logger.info(
        f"deliver_document: doc_id={doc_id}, version_id={version_id}"
    )
    
    # Emit run.started if not already marked as running
    emit_run_started(run_id, trace_id)
    
    try:
        import json
        from jobs_engine.utils.minio_artifact_handler import download_artifact
        from models.document_version import DocumentVersion
        from models.delivery_event import DeliveryEvent, DeliveryStatus

        # Fetch DocumentVersion and load parsed content
        with SessionLocalSync() as db:
            doc_version = db.get(DocumentVersion, version_id)
            if not doc_version:
                raise ValueError(f"DocumentVersion {version_id} not found")

            logger.info(f"Loading parsed document from {doc_version.parsed_uri}")
            parsed_json_bytes = download_artifact(doc_version.parsed_uri)
            parsed_document = json.loads(parsed_json_bytes.decode('utf-8'))

            # Create DeliveryEvent record
            delivery_event = DeliveryEvent(
                doc_version_id=version_id,
                status=DeliveryStatus.PENDING,  
                artifact_type="parsed_document",
            )
            db.add(delivery_event)
            db.flush()
            delivery_event_id = delivery_event.id
            logger.info(f"Created DeliveryEvent: id={delivery_event_id}")
            db.commit()

        # Emit delivery.request event for downstream consumption
        delivery_request_payload = {
            "doc_id": doc_id,
            "version_id": version_id,
            "parsed_document": parsed_document,
            "run_id": run_id,
            "trace_id": trace_id,
        }

        logger.info(
            f"Emitting delivery.request for doc_id={doc_id}, version_id={version_id} "
            f"with {len(parsed_document.get('sections', []))} sections"
        )
        emit_event("delivery.request", delivery_request_payload, topic="delivery.request")

        # Emit delivery.result event to complete the delivery stage
        delivery_result_payload = {
            "doc_id": doc_id,
            "version_id": version_id,
            "status": "COMPLETED",
            "result": {
                "delivery_event_id": delivery_event_id,
                "sections_delivered": len(parsed_document.get('sections', [])),
            },
            "run_id": run_id,
            "trace_id": trace_id,
        }

        emit_event("delivery.result", delivery_result_payload, topic="delivery.result")

        # Update DeliveryEvent status to COMPLETED
        with SessionLocalSync() as db:
            delivery_event = db.get(DeliveryEvent, delivery_event_id)
            if delivery_event:
                delivery_event.status = DeliveryStatus.COMPLETED
                delivery_event.delivery_uri = doc_version.parsed_uri
                db.commit()
                logger.info(f"Updated DeliveryEvent {delivery_event_id} to COMPLETED")

        logger.info(
            f"Successfully delivered document: doc_id={doc_id}, "
            f"version_id={version_id}, delivery_event_id={delivery_event_id}"
        )

        # Emit run.completed event
        emit_run_completed(run_id, trace_id)

        return delivery_result_payload

    except Exception as e:
        logger.exception(f"Error delivering document {doc_id}: {e}")
        # Emit run.failed event - halts the pipeline
        emit_run_failed(run_id, trace_id, str(e), traceback.format_exc())
        raise

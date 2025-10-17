"""MinIO artifact handler utilities for parse pipeline."""

import json
import logging
from io import BytesIO
from typing import Any, Dict

from jobs_engine.minio_client import MinIOClient
from minio.error import S3Error

logger = logging.getLogger(__name__)


def download_artifact(blob_uri: str) -> bytes:
    """Download an artifact from MinIO by URI.

    Args:
        blob_uri: URI like s3://artifacts/raw/{source}/{yyyy}/{mm}/{dd}/{sha256}.bin

    Returns:
        Raw bytes of the artifact

    Raises:
        ValueError: If download fails
    """
    try:
        # Parse URI: s3://artifacts/path/to/object
        if not blob_uri.startswith("s3://artifacts/"):
            raise ValueError(f"Invalid artifact URI: {blob_uri}")

        object_key = blob_uri.replace("s3://artifacts/", "")

        minio = MinIOClient()
        response = minio.client.get_object("artifacts", object_key)
        data = response.read()
        response.close()

        logger.info(f"Downloaded artifact: {blob_uri} ({len(data)} bytes)")
        return data

    except S3Error as e:
        logger.exception(f"MinIO error downloading {blob_uri}: {e}")
        raise ValueError(f"Failed to download artifact: {e}")
    except Exception as e:
        logger.exception(f"Error downloading artifact {blob_uri}: {e}")
        raise


def upload_parsed_document(
    doc_id: int, version_id: int, parsed_doc: Dict[str, Any]
) -> str:
    """Upload parsed document JSON to MinIO.

    Args:
        doc_id: Document ID
        version_id: Document version ID
        parsed_doc: Parsed document dict

    Returns:
        S3 URI of uploaded document

    Raises:
        ValueError: If upload fails
    """
    try:
        minio = MinIOClient()
        
        # Create object key: parsed/{doc_id}/{version_id}.json
        object_key = f"parsed/{doc_id}/{version_id}.json"

        # Serialize to JSON
        json_data = json.dumps(parsed_doc, indent=2)
        data_bytes = json_data.encode("utf-8")

        # Upload
        data_stream = BytesIO(data_bytes)
        minio.client.put_object(
            bucket_name="artifacts",
            object_name=object_key,
            data=data_stream,
            length=len(data_bytes),
            content_type="application/json",
        )

        uri = f"s3://artifacts/{object_key}"
        logger.info(f"Uploaded parsed document: {uri}")
        return uri

    except S3Error as e:
        logger.exception(f"MinIO error uploading parsed document: {e}")
        raise ValueError(f"Failed to upload parsed document: {e}")
    except Exception as e:
        logger.exception(f"Error uploading parsed document: {e}")
        raise


def upload_raw_metadata(sha256: str, metadata: Dict[str, Any]) -> str:
    """Upload raw artifact metadata to MinIO.

    Args:
        sha256: SHA256 hash of raw artifact
        metadata: Metadata dict

    Returns:
        S3 URI of uploaded metadata

    Raises:
        ValueError: If upload fails
    """
    try:
        minio = MinIOClient()
        
        # Create object key: raw_meta/{sha256}.json
        object_key = f"raw_meta/{sha256}.json"

        # Serialize to JSON
        json_data = json.dumps(metadata, indent=2)
        data_bytes = json_data.encode("utf-8")

        # Upload
        data_stream = BytesIO(data_bytes)
        minio.client.put_object(
            bucket_name="artifacts",
            object_name=object_key,
            data=data_stream,
            length=len(data_bytes),
            content_type="application/json",
        )

        uri = f"s3://artifacts/{object_key}"
        logger.info(f"Uploaded raw metadata: {uri}")
        return uri

    except S3Error as e:
        logger.exception(f"MinIO error uploading metadata: {e}")
        raise ValueError(f"Failed to upload metadata: {e}")
    except Exception as e:
        logger.exception(f"Error uploading metadata: {e}")
        raise

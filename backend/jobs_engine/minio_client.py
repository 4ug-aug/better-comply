"""MinIO client configuration for job result submission."""

import json
import os
from datetime import datetime
from io import BytesIO
from uuid import UUID
from minio import Minio
from minio.error import S3Error

class MinIOClient:
    """MinIO client wrapper for OSINT result submission."""
    
    def __init__(self):
        """Initialize MinIO client with environment configuration."""
        self.endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
        
        self.bucket_name = "osint-sink"
        self.artifacts_bucket = "artifacts"
    
    def ensure_bucket_exists(self, bucket_name: str = None) -> bool:
        """Ensure a bucket exists, create if it doesn't.
        
        Args:
            bucket_name: Bucket name to check. If None, uses self.bucket_name.
            
        Returns:
            True if bucket exists or was created successfully.
        """
        bucket = bucket_name or self.bucket_name
        try:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                return True
            return True
        except S3Error as e:
            print(f"Error ensuring bucket exists: {e}")
            return False
    
    def submit_job_result(self, job_id: UUID, result_data: dict) -> object:
        """Submit job result JSON to MinIO osint-sink bucket.
        
        Args:
            job_id: Unique identifier for the job
            result_data: Dictionary containing the job result data
            
        Returns:
            object: Object if successful, None otherwise
        """
        try:
            # Ensure bucket exists
            if not self.ensure_bucket_exists():
                return None
            
            # Convert job_id to string
            job_id_str = str(job_id)
            
            # Create object name with job_id and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            object_name = f"job_results/{job_id_str}_{timestamp}.json"
            
            # Serialize result_data to JSON and create BytesIO object
            json_data = json.dumps(result_data, indent=2)
            data_bytes = BytesIO(json_data.encode('utf-8'))
            
            # Upload to MinIO
            object = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=data_bytes,
                length=len(json_data.encode('utf-8')),
                content_type="application/json"
            )
            
            print(f"Successfully submitted job result for {job_id} to {object_name}")
            return object
            
        except S3Error as e:
            print(f"MinIO S3 error submitting job result: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error submitting job result: {e}")
            return None
    
    def upload_artifact(
        self,
        bucket_name: str,
        object_key: str,
        data: bytes,
        content_type: str = "application/octet-stream"
    ) -> bool:
        """Upload an artifact to MinIO.
        
        Args:
            bucket_name: Target bucket name
            object_key: Object key/path in bucket
            data: Raw bytes to upload
            content_type: MIME type of the content
            
        Returns:
            True if upload was successful, False otherwise
        """
        try:
            # Ensure bucket exists
            if not self.ensure_bucket_exists(bucket_name):
                return False
            
            data_stream = BytesIO(data)
            
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_key,
                data=data_stream,
                length=len(data),
                content_type=content_type,
            )
            
            print(f"Successfully uploaded artifact: s3://{bucket_name}/{object_key}")
            return True
            
        except S3Error as e:
            print(f"MinIO S3 error uploading artifact: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error uploading artifact: {e}")
            return False


# Global instance for easy access
minio_client = MinIOClient()

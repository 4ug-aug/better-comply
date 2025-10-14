"""Pydantic models for Kafka events.

This module contains Pydantic models for various event types that are consumed
from Kafka, including MinIO S3 events and other domain events.
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class UserIdentity(BaseModel):
    """User identity information from MinIO events."""
    principalId: str


class RequestParameters(BaseModel):
    """Request parameters from MinIO events."""
    principalId: str
    region: str
    sourceIPAddress: str


class BucketOwnerIdentity(BaseModel):
    """Bucket owner identity information."""
    principalId: str


class BucketInfo(BaseModel):
    """Bucket information from S3 events."""
    name: str
    ownerIdentity: BucketOwnerIdentity
    arn: str


class ObjectUserMetadata(BaseModel):
    """User metadata for S3 objects."""
    content_type: str = Field(alias="content-type")


class ObjectInfo(BaseModel):
    """S3 object information from events."""
    key: str
    size: int
    eTag: str
    contentType: str
    userMetadata: ObjectUserMetadata
    sequencer: str


class S3Info(BaseModel):
    """S3-specific information from events."""
    s3SchemaVersion: str
    configurationId: str
    bucket: BucketInfo
    object: ObjectInfo


class SourceInfo(BaseModel):
    """Source information from MinIO events."""
    host: str
    port: str
    userAgent: str


class MinIORecord(BaseModel):
    """Individual record from MinIO S3 event."""
    eventVersion: str
    eventSource: str
    awsRegion: str
    eventTime: datetime
    eventName: str
    userIdentity: UserIdentity
    requestParameters: RequestParameters
    responseElements: dict
    s3: S3Info
    source: SourceInfo


class MinIOS3Event(BaseModel):
    """Complete MinIO S3 event structure from Kafka."""
    EventName: str
    Key: str
    Records: List[MinIORecord]

    class Config:
        """Pydantic configuration."""
        # Allow field aliases for JSON parsing
        allow_population_by_field_name = True
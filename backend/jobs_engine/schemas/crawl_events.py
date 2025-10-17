from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class SubscriptionScheduledData(BaseModel):
    """Data for subs.schedule events from the scheduling system."""
    subscription_id: int
    run_id: int


class SubscriptionScheduledEvent(BaseModel):
    """Event emitted when a subscription is due to run."""
    event: str  # "subs.schedule"
    data: SubscriptionScheduledData


class CrawlRequestPayload(BaseModel):
    """Payload for crawl.request events."""
    url: str
    source_id: int
    run_id: int
    crawl_request_id: str
    trace_id: str
    subscription_id: int


class CrawlResultPayload(BaseModel):
    """Payload for crawl.result events."""
    artifact_id: int
    blob_uri: str
    content_type: str
    status_code: int
    headers: Dict[str, Any]
    run_id: int
    trace_id: str
    source_url: str


class ParseRequestPayload(BaseModel):
    """Placeholder for parse.request events."""
    artifact_id: int
    blob_uri: str
    run_id: int
    trace_id: str


class VersioningRequestPayload(BaseModel):
    """Placeholder for versioning.request events."""
    parse_result_id: int
    run_id: int
    trace_id: str


class VersioningResultPayload(BaseModel):
    """Payload for versioning.result events."""
    doc_id: int
    version_id: int
    diff_uri: Optional[str]  # NULL for first version
    run_id: int
    trace_id: str


class DeliveryRequestPayload(BaseModel):
    """Payload for delivery.request events."""
    doc_id: int
    version_id: int
    parsed_document: Dict[str, Any]  # Full parsed document JSON
    run_id: int
    trace_id: str


class DeliveryResultPayload(BaseModel):
    """Payload for delivery.result events."""
    doc_id: int
    version_id: int
    status: str  # "COMPLETED" or "FAILED"
    result: Optional[Dict[str, Any]] = None  # Delivery metadata/result
    run_id: int
    trace_id: str

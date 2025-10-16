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


class DeliveryRequestPayload(BaseModel):
    """Placeholder for delivery.request events."""
    version_id: int
    run_id: int
    trace_id: str

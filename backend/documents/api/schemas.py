"""Pydantic schemas for documents API."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel


class DocumentVersionOut(BaseModel):
    """Document version response model."""

    id: int
    document_id: int
    parsed_uri: str
    diff_uri: Optional[str]
    content_hash: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentOut(BaseModel):
    """Document response model."""

    id: int
    source_id: int
    source_url: str
    published_date: Optional[str]
    language: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentDetailOut(BaseModel):
    """Document with nested versions response model."""

    id: int
    source_id: int
    source_url: str
    published_date: Optional[str]
    language: str
    created_at: datetime
    updated_at: datetime
    versions: List[DocumentVersionOut]
    version_count: int

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Paginated documents list response."""

    items: List[DocumentOut]
    total: int
    skip: int
    limit: int


class DocumentDetailListResponse(BaseModel):
    """Paginated documents with versions list response."""

    items: List[DocumentDetailOut]
    total: int
    skip: int
    limit: int


class ParsedDocumentOut(BaseModel):
    """Parsed document content response model.
    
    Contains the full parsed HTML content with sections and metadata.
    """

    source_url: str
    published_date: Optional[str]
    language: str
    fetch_timestamp: str
    sections: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class AuditTrailEventOut(BaseModel):
    """Audit trail event response model."""

    event_type: str
    event_id: int
    timestamp: datetime
    status: str
    run_id: Optional[int]
    run_kind: Optional[str]
    artifact_ids: List[int]
    artifact_uris: List[str]
    version_id: Optional[int]
    parsed_uri: Optional[str]
    diff_uri: Optional[str]
    content_hash: Optional[str]
    error: Optional[str]

    class Config:
        from_attributes = True


class DocumentAuditTrailResponse(BaseModel):
    """Document audit trail response containing all processing events."""

    document_id: int
    source_url: str
    events: List[AuditTrailEventOut]

    class Config:
        from_attributes = True

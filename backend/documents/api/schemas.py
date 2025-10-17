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

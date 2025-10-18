"""Data transfer objects for documents and versions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass(frozen=True)
class DocumentVersionDTO:
    """Document version data transfer object."""

    id: int
    document_id: int
    parsed_uri: str
    diff_uri: Optional[str]
    content_hash: str
    created_at: datetime


@dataclass(frozen=True)
class DocumentDTO:
    """Document data transfer object."""

    id: int
    source_id: int
    source_url: str
    published_date: Optional[str]
    language: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class DocumentWithVersionsDTO:
    """Document with all its versions."""

    document: DocumentDTO
    versions: List[DocumentVersionDTO]
    version_count: int


@dataclass(frozen=True)
class AuditTrailEventDTO:
    """Audit trail event data transfer object."""

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

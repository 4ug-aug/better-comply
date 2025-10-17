"""Parse pipeline event schemas for HTML parsing results."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class TableData(BaseModel):
    """Structured table data from HTML."""

    type: str  # "csv", "structured", etc.
    headers: List[str]
    rows: List[List[str]]


class ParsedSection(BaseModel):
    """A section of parsed HTML content."""

    id: int
    level: int  # 1-4 for H1-H4
    heading: str
    text: str
    sha256: str  # SHA256 of section text
    byte_offset_start: int
    byte_offset_end: int
    tables: List[TableData] = []
    language: str = "en"


class ParsedDocument(BaseModel):
    """Complete parsed HTML document."""

    source_url: str
    published_date: Optional[str] = None
    language: str = "en"
    fetch_timestamp: str  # ISO format
    sections: List[ParsedSection]


class ParseResultPayload(BaseModel):
    """Payload for parse.result events."""

    doc_id: int
    version_id: int
    parsed_uri: str  # s3://artifacts/parsed/{doc_id}/{version_id}.json
    section_count: int
    run_id: int
    trace_id: str
    source_url: str

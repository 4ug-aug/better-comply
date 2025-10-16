from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field


class SourceOut(BaseModel):
    id: int
    name: str
    kind: Literal['html', 'api', 'pdf']
    base_url: str
    auth_ref: Optional[str] = None
    robots_mode: Literal['allow', 'disallow', 'custom'] = 'allow'
    rate_limit: int = 60
    enabled: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CreateSourceRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    kind: Literal['html', 'api', 'pdf']
    base_url: str = Field(..., min_length=1)
    auth_ref: Optional[str] = Field(None, max_length=255)
    robots_mode: Literal['allow', 'disallow', 'custom'] = 'allow'
    rate_limit: int = Field(default=60, ge=1, le=3600)
    enabled: bool = True


class UpdateSourceRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    kind: Optional[Literal['html', 'api', 'pdf']] = None
    base_url: Optional[str] = Field(None, min_length=1)
    auth_ref: Optional[str] = Field(None, max_length=255)
    robots_mode: Optional[Literal['allow', 'disallow', 'custom']] = None
    rate_limit: Optional[int] = Field(None, ge=1, le=3600)
    enabled: Optional[bool] = None


class SourceResponse(SourceOut):
    pass


class SourceDetailOut(SourceOut):
    pass

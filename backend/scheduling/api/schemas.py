from __future__ import annotations

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class BatchRequest(BaseModel):
    batch_size: int = Field(default=100, ge=1, le=5000)


class TickResult(BaseModel):
    processed: int


class ComputeNextResult(BaseModel):
    updated: int


class DispatchResult(BaseModel):
    published: int


class SubscriptionOut(BaseModel):
    id: int
    schedule: str
    last_run_at: Optional[str] = None
    next_run_at: Optional[str] = None
    status: str


class RunOut(BaseModel):
    id: int
    subscription_id: int
    run_kind: str
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    status: str


class OutboxOut(BaseModel):
    id: int
    created_at: Optional[str] = None
    event_type: str
    payload: Dict[str, Any]
    status: str
    attempts: int
    published_at: Optional[str] = None


class CreateSubscriptionRequest(BaseModel):
    source_id: int
    jurisdiction: str
    selectors: Dict[str, Any]
    schedule: str
    status: Literal['ACTIVE', 'DISABLED'] = 'ACTIVE'


class SubscriptionResponse(SubscriptionOut):
    pass



class SubscriptionDetailOut(BaseModel):
    id: int
    source_id: int
    jurisdiction: str
    selectors: Dict[str, Any]
    schedule: str
    last_run_at: Optional[str] = None
    next_run_at: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


"""Run status event schemas for tracking task execution lifecycle."""

from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel


class RunStartedPayload(BaseModel):
    """Payload for run.started events."""

    run_id: int
    trace_id: str


class RunCompletedPayload(BaseModel):
    """Payload for run.completed events."""

    run_id: int
    trace_id: str
    result: Optional[Dict[str, Any]] = None


class RunFailedPayload(BaseModel):
    """Payload for run.failed events."""

    run_id: int
    trace_id: str
    error_message: str
    error_traceback: Optional[str] = None

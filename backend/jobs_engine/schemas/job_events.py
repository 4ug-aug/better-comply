from __future__ import annotations

from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel


class JobRequestedData(BaseModel):
    job_id: str
    type: str
    payload: Dict[str, Any] = {}
    requested_at: datetime


class JobRequested(BaseModel):
    event: str
    data: JobRequestedData


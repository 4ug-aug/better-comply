from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class OutboxItem:
    id: int
    event_type: str
    payload: Dict[str, Any]



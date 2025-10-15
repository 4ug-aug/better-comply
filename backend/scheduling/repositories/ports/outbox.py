from __future__ import annotations

from typing import Protocol, List, Dict, Any
from datetime import datetime
from scheduling.repositories.dto import OutboxItem


class OutboxPort(Protocol):
    def enqueue(self, event_type: str, payload: Dict[str, Any]) -> int:
        ...

    def fetch_pending_for_update(self, limit: int) -> List[OutboxItem]:
        ...

    def mark_published(self, ids: List[int], now: datetime) -> int:
        ...

    def increment_attempt(self, id: int) -> None:
        ...



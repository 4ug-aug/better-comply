from __future__ import annotations

from typing import Protocol, List
from datetime import datetime


class SubscriptionsPort(Protocol):
    def pick_and_mark_due(self, now: datetime, limit: int) -> List[int]:
        ...

    def fill_next_run(self, now: datetime, limit: int) -> int:
        ...



from __future__ import annotations

from typing import Protocol
from datetime import datetime


class RunsPort(Protocol):
    def create_schedule_run(self, subscription_id: int, now: datetime) -> int:
        ...



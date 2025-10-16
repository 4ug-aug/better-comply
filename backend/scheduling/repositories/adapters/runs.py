from __future__ import annotations

from datetime import datetime
from models.run import Run, RunKind, RunStatus


class RunsAdapter:
    def __init__(self, db):
        self.db = db

    def create_schedule_run(self, subscription_id: int, now: datetime) -> int:
        run = Run(
            subscription_id=subscription_id,
            run_kind=RunKind.SCHEDULE,
            started_at=now,
            status=RunStatus.PENDING,
        )
        self.db.add(run)
        self.db.flush()
        return run.id



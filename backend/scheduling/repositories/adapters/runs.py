from __future__ import annotations

from datetime import datetime
from sqlalchemy import text


class RunsAdapter:
    def __init__(self, db):
        self.db = db

    def create_schedule_run(self, subscription_id: int, now: datetime) -> int:
        row = self.db.execute(
            text(
                """
                INSERT INTO runs(subscription_id, run_kind, started_at, status)
                VALUES(:sid, 'SCHEDULE', :now, 'PENDING')
                RETURNING id
                """
            ),
            {"sid": subscription_id, "now": now},
        ).fetchone()
        return row[0]



from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import text


class SubscriptionsAdapter:
    def __init__(self, db):
        self.db = db

    def pick_and_mark_due(self, now: datetime, limit: int) -> List[int]:
        rows = self.db.execute(
            text(
                """
                WITH due AS (
                  SELECT id
                  FROM subscriptions
                  WHERE status = 'ACTIVE'
                    AND (next_run_at IS NULL OR next_run_at <= :now)
                  ORDER BY next_run_at NULLS FIRST
                  FOR UPDATE SKIP LOCKED
                  LIMIT :limit
                )
                UPDATE subscriptions s
                SET last_run_at = :now,
                    next_run_at = NULL
                FROM due
                WHERE s.id = due.id
                RETURNING s.id
                """
            ),
            {"now": now, "limit": limit},
        ).fetchall()
        return [r[0] for r in rows]

    def fill_next_run(self, now: datetime, limit: int) -> int:
        from croniter import croniter

        mappings = self.db.execute(
            text(
                """
                SELECT id, schedule, COALESCE(last_run_at, created_at, :now) AS base
                FROM subscriptions
                WHERE next_run_at IS NULL AND status = 'ACTIVE'
                LIMIT :limit
                """
            ),
            {"now": now, "limit": limit},
        ).mappings().all()

        changed = 0
        for r in mappings:
            nxt = croniter(r["schedule"], r["base"]).get_next(datetime)
            self.db.execute(
                text("UPDATE subscriptions SET next_run_at = :nxt WHERE id = :id"),
                {"nxt": nxt, "id": r["id"]},
            )
            changed += 1
        return changed



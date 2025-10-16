from __future__ import annotations

from typing import List, Optional, Dict, Any
from sqlalchemy import text


class QueriesAdapter:
    def __init__(self, db):
        self.db = db

    def list_subscriptions(self, status: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
        if status:
            rows = self.db.execute(
                text(
                    """
                    SELECT id, schedule, last_run_at, next_run_at, status
                    FROM subscriptions
                    WHERE status = :status
                    ORDER BY id DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {"status": status, "limit": limit, "offset": offset},
            ).mappings().all()
        else:
            rows = self.db.execute(
                text(
                    """
                    SELECT id, schedule, last_run_at, next_run_at, status
                    FROM subscriptions
                    ORDER BY id DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {"limit": limit, "offset": offset},
            ).mappings().all()
        return [dict(r) for r in rows]

    def list_runs(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        rows = self.db.execute(
            text(
                """
                SELECT id, subscription_id, run_kind, started_at, ended_at, status
                FROM runs
                ORDER BY id DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            {"limit": limit, "offset": offset},
        ).mappings().all()
        return [dict(r) for r in rows]

    def list_outbox(self, status: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
        if status:
            rows = self.db.execute(
                text(
                    """
                    SELECT id, created_at, event_type, payload, status, attempts, published_at
                    FROM outbox
                    WHERE status = :status
                    ORDER BY id DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {"status": status, "limit": limit, "offset": offset},
            ).mappings().all()
        else:
            rows = self.db.execute(
                text(
                    """
                    SELECT id, created_at, event_type, payload, status, attempts, published_at
                    FROM outbox
                    ORDER BY id DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {"limit": limit, "offset": offset},
            ).mappings().all()
        return [dict(r) for r in rows]



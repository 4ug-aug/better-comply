from __future__ import annotations

from datetime import datetime
from typing import List
import json

from sqlalchemy import text

from scheduling.repositories.dto import OutboxItem


class OutboxAdapter:
    def __init__(self, db):
        self.db = db

    def enqueue(self, event_type: str, payload: dict) -> int:
        pj = json.dumps(payload)
        row = self.db.execute(
            text(
                """
                INSERT INTO outbox(event_type, payload, status)
                VALUES(:etype, :payload::jsonb, 'PENDING')
                RETURNING id
                """
            ),
            {"etype": event_type, "payload": pj},
        ).fetchone()
        return row[0]

    def fetch_pending_for_update(self, limit: int) -> List[OutboxItem]:
        rows = self.db.execute(
            text(
                """
                SELECT id, event_type, payload::text AS payload
                FROM outbox
                WHERE status = 'PENDING'
                ORDER BY id
                FOR UPDATE SKIP LOCKED
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).fetchall()
        items: List[OutboxItem] = []
        for oid, event_type, payload_text in rows:
            items.append(OutboxItem(id=oid, event_type=event_type, payload=json.loads(payload_text)))
        return items

    def mark_published(self, ids: List[int], now: datetime) -> int:
        if not ids:
            return 0
        self.db.execute(
            text(
                """
                UPDATE outbox
                SET status='PUBLISHED', published_at=:now
                WHERE id = ANY(:ids)
                """
            ),
            {"now": now, "ids": ids},
        )
        return len(ids)

    def increment_attempt(self, id: int) -> None:
        self.db.execute(text("UPDATE outbox SET attempts = attempts + 1 WHERE id = :id"), {"id": id})



from __future__ import annotations

from datetime import datetime
from typing import List
import json

from sqlalchemy import select

from scheduling.repositories.dto import OutboxItem
from models.outbox import Outbox, OutboxStatus


class OutboxAdapter:
    def __init__(self, db):
        self.db = db

    def enqueue(self, event_type: str, payload: dict) -> int:
        item = Outbox(event_type=event_type, payload=payload, status=OutboxStatus.PENDING)
        self.db.add(item)
        self.db.flush()
        return item.id

    def fetch_pending_for_update(self, limit: int) -> List[OutboxItem]:
        q = (
            select(Outbox)
            .where(Outbox.status == OutboxStatus.PENDING)
            .order_by(Outbox.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        rows = self.db.execute(q).scalars().all()
        return [OutboxItem(id=r.id, event_type=r.event_type, payload=r.payload) for r in rows]

    def mark_published(self, ids: List[int], now: datetime) -> int:
        if not ids:
            return 0
        for oid in ids:
            row = self.db.get(Outbox, oid)
            if row:
                row.status = OutboxStatus.PUBLISHED
                row.published_at = now
        return len(ids)

    def increment_attempt(self, id: int) -> None:
        row = self.db.get(Outbox, id)
        if row:
            row.attempts = (row.attempts or 0) + 1



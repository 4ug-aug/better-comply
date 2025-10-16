from __future__ import annotations

from typing import List, Optional, Dict, Any
from sqlalchemy import select
from models.subscription import Subscription
from models.run import Run
from models.outbox import Outbox


class QueriesAdapter:
    def __init__(self, db):
        self.db = db

    def list_subscriptions(self, status: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
        q = select(Subscription).order_by(Subscription.id.desc()).limit(limit).offset(offset)
        if status:
            q = q.where(Subscription.status == status)
        subs = self.db.execute(q).scalars().all()
        return [
            {
                "id": s.id,
                "schedule": s.schedule,
                "last_run_at": s.last_run_at.isoformat() if s.last_run_at else None,
                "next_run_at": s.next_run_at.isoformat() if s.next_run_at else None,
                "status": s.status.name if hasattr(s.status, "name") else s.status,
            }
            for s in subs
        ]

    def list_runs(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        q = select(Run).order_by(Run.id.desc()).limit(limit).offset(offset)
        runs = self.db.execute(q).scalars().all()
        return [
            {
                "id": r.id,
                "subscription_id": r.subscription_id,
                "run_kind": r.run_kind.name if hasattr(r.run_kind, "name") else r.run_kind,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "ended_at": r.ended_at.isoformat() if r.ended_at else None,
                "status": r.status.name if hasattr(r.status, "name") else r.status,
            }
            for r in runs
        ]

    def list_outbox(self, status: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
        q = select(Outbox).order_by(Outbox.id.desc()).limit(limit).offset(offset)
        if status:
            q = q.where(Outbox.status == status)
        rows = self.db.execute(q).scalars().all()
        return [
            {
                "id": o.id,
                "created_at": o.created_at.isoformat() if o.created_at else None,
                "event_type": o.event_type,
                "payload": o.payload,
                "status": o.status.name if hasattr(o.status, "name") else o.status,
                "attempts": o.attempts,
                "published_at": o.published_at.isoformat() if o.published_at else None,
            }
            for o in rows
        ]



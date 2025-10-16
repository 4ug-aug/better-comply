from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import select

from models.subscription import Subscription, SubscriptionStatus


class SubscriptionsAdapter:
    def __init__(self, db):
        self.db = db

    def pick_and_mark_due(self, now: datetime, limit: int) -> List[int]:
        q = (
            select(Subscription)
            .where(
                Subscription.status == SubscriptionStatus.ACTIVE,
                ((Subscription.next_run_at.is_(None)) | (Subscription.next_run_at <= now)),
            )
            .order_by(Subscription.next_run_at.asc().nullsfirst())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        subs = self.db.execute(q).scalars().all()
        ids: List[int] = []
        for s in subs:
            s.last_run_at = now
            s.next_run_at = None
            ids.append(s.id)
        return ids

    def fill_next_run(self, now: datetime, limit: int) -> int:
        from croniter import croniter

        q = (
            select(Subscription)
            .where(Subscription.next_run_at.is_(None), Subscription.status == SubscriptionStatus.ACTIVE)
            .order_by(Subscription.id.desc())
            .limit(limit)
        )
        subs = self.db.execute(q).scalars().all()

        changed = 0
        for s in subs:
            base = s.last_run_at or s.created_at or now
            nxt = croniter(s.schedule, base).get_next(datetime)
            s.next_run_at = nxt
            changed += 1
        return changed



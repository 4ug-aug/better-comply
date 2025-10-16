from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from database.sync import SessionLocalSync
from events.kafka_emitter import emit_event
from scheduling.repositories.adapters.subscriptions import SubscriptionsAdapter
from scheduling.repositories.adapters.runs import RunsAdapter
from scheduling.repositories.adapters.outbox import OutboxAdapter
from scheduling.repositories.adapters.queries import QueriesAdapter


@dataclass
class SchedulingService:
    def tick(self, batch_size: int) -> int:
        now = datetime.now(timezone.utc)
        processed = 0
        with SessionLocalSync() as db:
            subs_repo = SubscriptionsAdapter(db)
            runs_repo = RunsAdapter(db)
            outbox_repo = OutboxAdapter(db)

            due_ids = subs_repo.pick_and_mark_due(now=now, limit=batch_size)
            for sub_id in due_ids:
                run_id = runs_repo.create_schedule_run(subscription_id=sub_id, now=now)
                outbox_repo.enqueue("subs.schedule", {"subscription_id": sub_id, "run_id": run_id})
                processed += 1
            db.commit()
        return processed

    def compute_next(self, batch_size: int) -> int:
        now = datetime.now(timezone.utc)
        with SessionLocalSync() as db:
            subs_repo = SubscriptionsAdapter(db)
            updated = subs_repo.fill_next_run(now=now, limit=batch_size)
            db.commit()
            return updated

    def dispatch_outbox(self, batch_size: int) -> int:
        now = datetime.now(timezone.utc)
        published = 0
        with SessionLocalSync() as db:
            outbox_repo = OutboxAdapter(db)
            picked = outbox_repo.fetch_pending_for_update(limit=batch_size)
            for item in picked:
                ok = emit_event(item.event_type, item.payload)
                if ok:
                    outbox_repo.mark_published([item.id], now)
                    published += 1
                else:
                    outbox_repo.increment_attempt(item.id)
            db.commit()
        return published

    def list_subscriptions(self, status: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
        with SessionLocalSync() as db:
            q = QueriesAdapter(db)
            return q.list_subscriptions(status=status, limit=limit, offset=offset)

    def list_runs(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        with SessionLocalSync() as db:
            q = QueriesAdapter(db)
            return q.list_runs(limit=limit, offset=offset)

    def list_outbox(self, status: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
        with SessionLocalSync() as db:
            q = QueriesAdapter(db)
            return q.list_outbox(status=status, limit=limit, offset=offset)



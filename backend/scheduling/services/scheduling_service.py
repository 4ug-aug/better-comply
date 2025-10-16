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
from models.subscription import Subscription, SubscriptionStatus
from models.run import Run, RunKind, RunStatus
from models.outbox import Outbox, OutboxStatus
from scheduling.api.schemas import CreateSubscriptionRequest


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

    def get_subscription(self, sub_id: int) -> Dict[str, Any]:
        with SessionLocalSync() as db:
            sub = db.get(Subscription, sub_id)
            if not sub:
                return {}
            return {
                "id": sub.id,
                "source_id": sub.source_id,
                "jurisdiction": sub.jurisdiction,
                "selectors": sub.selectors,
                "schedule": sub.schedule,
                "last_run_at": sub.last_run_at.isoformat() if sub.last_run_at else None,
                "next_run_at": sub.next_run_at.isoformat() if sub.next_run_at else None,
                "status": sub.status.name if hasattr(sub.status, "name") else sub.status,
                "created_at": sub.created_at.isoformat() if sub.created_at else None,
                "updated_at": sub.updated_at.isoformat() if sub.updated_at else None,
            }

    # Actions (ORM-only)
    def create_subscription(self, req: CreateSubscriptionRequest) -> Dict[str, Any]:
        from croniter import croniter

        now = datetime.now(timezone.utc)
        with SessionLocalSync() as db:
            sub = Subscription(
                source_id=req.source_id,
                jurisdiction=req.jurisdiction,
                selectors=req.selectors,
                schedule=req.schedule,
                status=SubscriptionStatus[req.status],
            )
            db.add(sub)
            db.flush()

            base = sub.last_run_at or sub.created_at or now
            nxt = croniter(sub.schedule, base).get_next(datetime)
            sub.next_run_at = nxt

            db.commit()
            return {
                "id": sub.id,
                "schedule": sub.schedule,
                "last_run_at": sub.last_run_at.isoformat() if sub.last_run_at else None,
                "next_run_at": sub.next_run_at.isoformat() if sub.next_run_at else None,
                "status": sub.status.name,
            }

    def set_subscription_status(self, sub_id: int, status: str) -> Dict[str, Any]:
        with SessionLocalSync() as db:
            sub = db.get(Subscription, sub_id)
            if not sub:
                return {}
            sub.status = SubscriptionStatus[status]
            db.commit()
            return {
                "id": sub.id,
                "schedule": sub.schedule,
                "last_run_at": sub.last_run_at.isoformat() if sub.last_run_at else None,
                "next_run_at": sub.next_run_at.isoformat() if sub.next_run_at else None,
                "status": sub.status.name,
            }

    def run_subscription_now(self, sub_id: int) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        with SessionLocalSync() as db:
            sub = db.get(Subscription, sub_id)
            if not sub:
                return {}
            sub.last_run_at = now
            sub.next_run_at = None

            run = Run(subscription_id=sub.id, run_kind=RunKind.SCHEDULE, started_at=now, status=RunStatus.PENDING)
            db.add(run)
            db.flush()

            out = Outbox(event_type="subs.schedule", payload={"subscription_id": sub.id, "run_id": run.id}, status=OutboxStatus.PENDING)
            db.add(out)
            db.commit()
            return {
                "id": sub.id,
                "schedule": sub.schedule,
                "last_run_at": sub.last_run_at.isoformat() if sub.last_run_at else None,
                "next_run_at": sub.next_run_at.isoformat() if sub.next_run_at else None,
                "status": sub.status.name,
            }



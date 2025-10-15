# backend/tasks/scheduler.py
from celery import shared_task
from datetime import datetime, timezone
import random
import time
from database.sync import SessionLocalSync
from scheduling.repositories.adapters.subscriptions import SubscriptionsAdapter
from scheduling.repositories.adapters.runs import RunsAdapter
from scheduling.repositories.adapters.outbox import OutboxAdapter

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def tick(self, batch_size: int = 100):
    # jitter to reduce thundering herd
    time.sleep(random.uniform(0, 2))
    now = datetime.now(timezone.utc)
    with SessionLocalSync() as db:
        subs_repo = SubscriptionsAdapter(db)
        runs_repo = RunsAdapter(db)
        outbox_repo = OutboxAdapter(db)

        due_ids = subs_repo.pick_and_mark_due(now=now, limit=batch_size)
        for sub_id in due_ids:
            run_id = runs_repo.create_schedule_run(subscription_id=sub_id, now=now)
            outbox_repo.enqueue("subs.schedule", {"subscription_id": sub_id, "run_id": run_id})

        db.commit()

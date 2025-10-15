from celery import shared_task
import time
import random
from database.sync import SessionLocalSync
from scheduling.repositories.adapters.subscriptions import SubscriptionsAdapter


@shared_task(bind=True)
def compute_next_run(self, batch_size: int = 500):
    from datetime import datetime, timezone

    # jitter to reduce thundering herd
    time.sleep(random.uniform(0, 2))

    now = datetime.now(timezone.utc)
    with SessionLocalSync() as db:
        subs_repo = SubscriptionsAdapter(db)
        subs_repo.fill_next_run(now=now, limit=batch_size)
        db.commit()

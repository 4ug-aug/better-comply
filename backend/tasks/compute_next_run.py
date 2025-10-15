from celery import shared_task
import time
import random
from database.sync import SessionLocalSync


@shared_task(bind=True)
def compute_next_run(self, batch_size: int = 500):
    from croniter import croniter
    from sqlalchemy import text
    from datetime import datetime, timezone

    # jitter to reduce thundering herd
    time.sleep(random.uniform(0, 2))

    now = datetime.now(timezone.utc)
    with SessionLocalSync() as db:
        rows = db.execute(
            text(
                """
                SELECT id, schedule, COALESCE(last_run_at, created_at, :now) AS base
                FROM subscriptions
                WHERE next_run_at IS NULL AND status = 'ACTIVE'
                LIMIT :batch
                """
            ),
            {"now": now, "batch": batch_size},
        ).mappings().all()

        for r in rows:
            itr = croniter(r["schedule"], r["base"])
            nxt = itr.get_next(datetime)
            db.execute(
                text("UPDATE subscriptions SET next_run_at = :nxt WHERE id = :id"),
                {"nxt": nxt, "id": r["id"]},
            )
        db.commit()

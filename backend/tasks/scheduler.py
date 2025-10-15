# backend/tasks/scheduler.py
from celery import shared_task
from datetime import datetime, timezone
from sqlalchemy import text
from backend.database.connection import SessionLocal
from backend.outbox import enqueue_outbox_event  # inserts row in outbox table
from uuid import uuid4

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def tick(self, batch_size: int = 100):
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        # Pick due subscriptions using SKIP LOCKED
        rows = db.execute(text("""
            WITH due AS (
              SELECT id
              FROM subscription
              WHERE enabled = true
                AND (next_run_at IS NULL OR next_run_at <= :now)
              ORDER BY next_run_at NULLS FIRST
              FOR UPDATE SKIP LOCKED
              LIMIT :batch
            )
            UPDATE subscription s
            SET last_run_at = :now,
                next_run_at = NULL -- let compute_next_run fill this in later
            FROM due
            WHERE s.id = due.id
            RETURNING s.id
        """), {"now": now, "batch": batch_size}).fetchall()

        for (sub_id,) in rows:
            run_id = f"run_{uuid4().hex}"
            # Persist a 'run' row
            db.execute(text("""
                INSERT INTO run(id, subscription_id, run_kind, started_at, status)
                VALUES(:rid, :sid, 'schedule', :now, 'scheduled')
            """), {"rid": run_id, "sid": sub_id, "now": now})

            # Outbox message to publish to Kafka later
            enqueue_outbox_event(db,
                event_type="subs.schedule",
                payload={"subscription_id": sub_id, "run_id": run_id},
            )

        db.commit()

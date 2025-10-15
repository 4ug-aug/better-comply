# backend/tasks/scheduler.py
from celery import shared_task
from datetime import datetime, timezone
import json
import random
import time
from sqlalchemy import text
from database.sync import SessionLocalSync

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def tick(self, batch_size: int = 100):
    # jitter to reduce thundering herd
    time.sleep(random.uniform(0, 2))
    now = datetime.now(timezone.utc)
    with SessionLocalSync() as db:
        # Pick due subscriptions using SKIP LOCKED
        rows = db.execute(text(
            """
            WITH due AS (
              SELECT id
              FROM subscriptions
              WHERE status = 'ACTIVE'
                AND (next_run_at IS NULL OR next_run_at <= :now)
              ORDER BY next_run_at NULLS FIRST
              FOR UPDATE SKIP LOCKED
              LIMIT :batch
            )
            UPDATE subscriptions s
            SET last_run_at = :now,
                next_run_at = NULL -- let compute_next_run fill this in later
            FROM due
            WHERE s.id = due.id
            RETURNING s.id
            """
        ), {"now": now, "batch": batch_size}).fetchall()

        for (sub_id,) in rows:
            # Persist a 'run' row and capture id
            run_row = db.execute(
                text(
                    """
                    INSERT INTO runs(subscription_id, run_kind, started_at, status)
                    VALUES(:sid, 'schedule', :now, 'PENDING')
                    RETURNING id
                    """
                ),
                {"sid": sub_id, "now": now},
            ).fetchone()
            run_id = run_row[0]

            # Outbox message to publish to Kafka later
            payload_json = json.dumps({"subscription_id": sub_id, "run_id": run_id})
            db.execute(
                text(
                    """
                    INSERT INTO outbox(event_type, payload, status)
                    VALUES(:etype, :payload::jsonb, 'PENDING')
                    """
                ),
                {"etype": "subs.schedule", "payload": payload_json},
            )

        db.commit()

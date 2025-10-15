from __future__ import annotations

from celery import shared_task
from datetime import datetime, timezone
import json
import random
import time
from typing import List, Tuple

from sqlalchemy import text

from database.sync import SessionLocalSync
from events.kafka_emitter import emit_event


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def dispatch_outbox(self, batch_size: int = 200) -> int:
    """Pick pending outbox rows, publish to Kafka, and mark published.

    Returns number of published messages.
    """
    # jitter to reduce thundering herd
    time.sleep(random.uniform(0, 1))

    now = datetime.now(timezone.utc)
    published_count = 0

    with SessionLocalSync() as db:
        # Lock a batch of pending events
        picked: List[Tuple[int, str, str]] = db.execute(
            text(
                """
                SELECT id, event_type, payload::text AS payload
                FROM outbox
                WHERE status = 'PENDING'
                ORDER BY id
                FOR UPDATE SKIP LOCKED
                LIMIT :batch
                """
            ),
            {"batch": batch_size},
        ).fetchall()

        for oid, event_type, payload_text in picked:
            payload = json.loads(payload_text) if isinstance(payload_text, str) else payload_text
            ok = emit_event(event_type, payload)
            if ok:
                db.execute(
                    text(
                        """
                        UPDATE outbox
                        SET status='published', published_at=:now
                        WHERE id=:id
                        """
                    ),
                    {"now": now, "id": oid},
                )
                published_count += 1
            else:
                db.execute(
                    text(
                        """
                        UPDATE outbox
                        SET attempts = attempts + 1
                        WHERE id = :id
                        """
                    ),
                    {"id": oid},
                )

        db.commit()

    return published_count



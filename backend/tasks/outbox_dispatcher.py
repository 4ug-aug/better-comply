from __future__ import annotations

from celery import shared_task
from datetime import datetime, timezone
import random
import time

from database.sync import SessionLocalSync
from events.kafka_emitter import emit_event
from scheduling.repositories.adapters.outbox import OutboxAdapter


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
        outbox_repo = OutboxAdapter(db)

        picked = outbox_repo.fetch_pending_for_update(limit=batch_size)

        for item in picked:
            event_type = item.event_type
            payload = item.payload
            ok = emit_event(event_type, payload, topic=event_type)
            if ok:
                outbox_repo.mark_published([item.id], now)
                published_count += 1
            else:
                outbox_repo.increment_attempt(item.id)

        db.commit()

    return published_count



#!/usr/bin/env python
"""Celery worker for Redcrawl with Kafka event consumer.

This script starts:
1. A Celery worker that processes enrichment and postprocess tasks
2. A Kafka consumer that reads 'jobs' topic and triggers appropriate tasks

Run with: python -m worker_main
"""

import logging
import sys
import threading
# Configure logging as early as possible
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

from jobs_engine.celery_app import app  # noqa: E402
from kafka import KafkaConsumer  # noqa: E402
from events.kafkaconfig import kafka_config  # noqa: E402
import jobs_engine.tasks # noqa: E402
from jobs_engine.schemas.job_events import JobRequested  # noqa: E402
from jobs_engine.routing import pick_task  # noqa: E402

logger = logging.getLogger(__name__)

def run_celery_worker():
    """Run the Celery worker in a separate thread."""
    logger.info("Starting Celery worker for task processing...")
    
    worker = app.Worker(
        loglevel="INFO",
        queues=["jobs"],
        pool="solo",  # Use solo pool for simpler async task handling
    )
    
    try:
        worker.start()
    except Exception as exc:
        logger.exception("Celery worker error: %s", exc)


def run_kafka_consumer():
    """Run the Kafka 'jobs' event consumer in a separate thread."""
    logger.info("Starting Kafka jobs consumer...")
    
    consumer = KafkaConsumer(**kafka_config)
    consumer.subscribe(["jobs"])
    logger.info("Kafka consumer subscribed to topic: jobs")
    try:
        for msg in consumer:
            logger.info("Kafka consumer received message: %s", msg)
            try:
                evt = JobRequested.model_validate_json(msg.value.decode())
            except Exception:
                logger.exception("Failed to parse job event JSON; skipping")
                continue

            if evt.event != "job.requested":
                logger.debug("Skipping non job.requested event: %s", evt.event)
                continue

            job_type = evt.data.type
            celery_task = pick_task(job_type)
            if not celery_task:
                logger.warning("Unknown job type: %s (job_id=%s)", job_type, evt.data.job_id)
                continue

            logger.info("Dispatching job_id=%s type=%s to task=%s", evt.data.job_id, job_type, celery_task)
            try:
                kwargs = dict(evt.data.payload or {})
                kwargs.setdefault("job_id", evt.data.job_id)
                logger.info("Sending task %s with kwargs %s", celery_task, kwargs)
                app.send_task(celery_task, kwargs=kwargs, queue="jobs")
            except Exception:
                logger.exception("Failed to dispatch job_id=%s type=%s", evt.data.job_id, job_type)
                continue
    finally:
        consumer.close()
        logger.info("Kafka jobs consumer stopped")


def main() -> int:
    """Start both Celery worker and Kafka consumer."""
    logger.info("=" * 60)
    logger.info("Starting Redcrawl Worker")
    logger.info("  - Celery worker: processes enrichment/postprocess tasks")
    logger.info("  - Kafka consumer: listens for 'jobs' events")
    logger.info("=" * 60)
    
    try:
        # Start Kafka consumer in a separate thread
        kafka_thread = threading.Thread(
            target=run_kafka_consumer,
            name="KafkaConsumer",
            daemon=True
        )
        kafka_thread.start()
        
        # Run Celery worker in main thread (blocks)
        run_celery_worker()
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        return 0
    
    except Exception as exc:
        logger.exception("Worker failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())



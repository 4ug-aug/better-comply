#!/usr/bin/env python
"""Celery worker for event-driven job handling with Kafka consumers.

This script starts:
1. A Celery worker that processes jobs from the jobs queue
2. Multiple Kafka consumer threads that listen to different event topics
   and route events to registered Celery tasks

Event consumers use the routing system to find registered tasks for each
job_type, enabling extensible event handling without hardcoding.

Run with: python -m jobs_engine.events_handler_worker
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
import jobs_engine.tasks.crawl_tasks  # noqa: E402, F401
import jobs_engine.tasks.run_status_tasks  # noqa: E402, F401
from jobs_engine.consumers.subscription_scheduled import (  # noqa: E402
    run_subscription_scheduled_consumer,
)
from jobs_engine.consumers.crawl_request import run_crawl_request_consumer  # noqa: E402
from jobs_engine.consumers.crawl_result import run_crawl_result_consumer  # noqa: E402
from jobs_engine.consumers.run_status import run_run_status_consumer  # noqa: E402
from jobs_engine.consumers.parse_result import run_parse_result_consumer  # noqa: E402
from jobs_engine.consumers.versioning_result import run_versioning_result_consumer  # noqa: E402
from jobs_engine.consumers.delivery_result import run_delivery_result_consumer  # noqa: E402

logger = logging.getLogger(__name__)


def run_celery_worker():
    """Run the Celery worker in the main thread."""
    logger.info("Starting Celery worker for job processing...")

    worker = app.Worker(
        loglevel="INFO",
        queues=["jobs"],
        pool="solo",  # Use solo pool for simpler async task handling
    )

    try:
        worker.start()
    except Exception as exc:
        logger.exception("Celery worker error: %s", exc)


def main() -> int:
    """Start Celery worker and all event consumers."""
    logger.info("=" * 60)
    logger.info("Starting Events Handler Worker")
    logger.info("  - Celery worker: processes jobs from jobs queue")
    logger.info("  - Event consumers: route Kafka events to registered tasks")
    logger.info("=" * 60)

    try:
        # Start subscription scheduled consumer thread
        subscription_consumer_thread = threading.Thread(
            target=run_subscription_scheduled_consumer,
            name="SubscriptionScheduledConsumer",
            daemon=True,
        )
        subscription_consumer_thread.start()
        logger.info("Started SubscriptionScheduledConsumer thread")

        # Start crawl request consumer thread
        crawl_request_consumer_thread = threading.Thread(
            target=run_crawl_request_consumer,
            name="CrawlRequestConsumer",
            daemon=True,
        )
        crawl_request_consumer_thread.start()
        logger.info("Started CrawlRequestConsumer thread")

        # Start crawl result consumer thread (scaffolded for parse phase)
        crawl_result_consumer_thread = threading.Thread(
            target=run_crawl_result_consumer,
            name="CrawlResultConsumer",
            daemon=True,
        )
        crawl_result_consumer_thread.start()
        logger.info("Started CrawlResultConsumer thread")

        # Start run status consumer thread
        run_status_consumer_thread = threading.Thread(
            target=run_run_status_consumer,
            name="RunStatusConsumer",
            daemon=True,
        )
        run_status_consumer_thread.start()
        logger.info("Started RunStatusConsumer thread")

        # Start parse result consumer thread
        parse_result_consumer_thread = threading.Thread(
            target=run_parse_result_consumer,
            name="ParseResultConsumer",
            daemon=True,
        )
        parse_result_consumer_thread.start()
        logger.info("Started ParseResultConsumer thread")

        # Start versioning result consumer thread
        versioning_result_consumer_thread = threading.Thread(
            target=run_versioning_result_consumer,
            name="VersioningResultConsumer",
            daemon=True,
        )
        versioning_result_consumer_thread.start()
        logger.info("Started VersioningResultConsumer thread")

        # Start delivery result consumer thread (terminal stage)
        delivery_result_consumer_thread = threading.Thread(
            target=run_delivery_result_consumer,
            name="DeliveryResultConsumer",
            daemon=True,
        )
        delivery_result_consumer_thread.start()
        logger.info("Started DeliveryResultConsumer thread")

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

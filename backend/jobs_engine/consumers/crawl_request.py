"""Consumer for crawl request events (crawl.request topic).

Listens to the crawl.request topic and routes events to the
crawl_url Celery task via routing system.
"""

import logging
from typing import Any, Dict

from events.event_consumer import GenericEventConsumer

logger = logging.getLogger(__name__)


def crawl_request_job_type_extractor(event: Dict[str, Any]) -> str:
    """Extract job_type from crawl request events.

    Args:
        event: Event dictionary from Kafka

    Returns:
        job_type string for routing to registered tasks
    """
    # crawl.request events should be routed to job_type="crawl.url"
    return "crawl.url"


class CrawlRequestConsumer(GenericEventConsumer):
    """Consumer for crawl.request events.

    Routes crawl request events to the registered crawl_url task.
    """

    def __init__(self):
        """Initialize crawl request consumer."""
        super().__init__(
            topic="crawl.request",
            job_type_extractor=crawl_request_job_type_extractor,
            consumer_name="CrawlRequestConsumer",
        )


def run_crawl_request_consumer() -> None:
    """Run the crawl request consumer.

    This subscribes to the crawl.request Kafka topic and routes events
    to the crawl_url task.
    """
    consumer = CrawlRequestConsumer()
    consumer.run()

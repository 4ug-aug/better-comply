"""Consumer for crawl result events (crawl.result topic).

This is a scaffolded consumer for the future parse phase implementation.
Currently routes crawl.result events to the parse_crawled_content task.

Once the parse phase is fully implemented, this consumer will trigger
document parsing when crawl results are available.
"""

import logging
from typing import Any, Dict

from events.event_consumer import GenericEventConsumer

logger = logging.getLogger(__name__)


def crawl_result_job_type_extractor(event: Dict[str, Any]) -> str:
    """Extract job_type from crawl result events.

    Args:
        event: Event dictionary from Kafka

    Returns:
        job_type string for routing to registered tasks
    """
    # crawl.result events should be routed to job_type="parse.content"
    # This will trigger the parse_crawled_content task
    return "parse.content"


class CrawlResultConsumer(GenericEventConsumer):
    """Consumer for crawl.result events.

    Routes crawl result events to the registered parse_crawled_content task
    (which will be implemented in the parse phase).
    """

    def __init__(self):
        """Initialize crawl result consumer."""
        super().__init__(
            topic="crawl.result",
            job_type_extractor=crawl_result_job_type_extractor,
            consumer_name="CrawlResultConsumer",
        )


def run_crawl_result_consumer() -> None:
    """Run the crawl result consumer.

    This subscribes to the crawl.result Kafka topic and routes events
    to the parse_crawled_content task (once implemented).

    Note: This is scaffolded for the future parse phase. The
    parse_crawled_content task currently raises NotImplementedError.
    """
    consumer = CrawlResultConsumer()
    consumer.run()

"""Consumer for crawl request events (crawl.request topic).

Listens to the crawl.request topic and routes events to the
crawl_url Celery task via routing system.
"""

import logging
from typing import Any, Dict

from events.event_consumer import GenericEventConsumer

logger = logging.getLogger(__name__)


class CrawlRequestConsumer(GenericEventConsumer):
    """Consumer for crawl.request events.

    Routes crawl request events to the registered crawl_url task.
    """

    def __init__(self):
        """Initialize crawl request consumer."""
        super().__init__(
            topic="crawl.request",
            job_type_extractor=self._job_type_extractor,
            event_payload_extractor=self._payload_extractor,
            consumer_name="CrawlRequestConsumer",
        )

    @staticmethod
    def _job_type_extractor(event: Dict[str, Any]) -> str:
        """Extract job_type from crawl request events.

        Args:
            event: Event dictionary from Kafka

        Returns:
            job_type string for routing to registered tasks
        """
        # crawl.request events should be routed to job_type="crawl.url"
        return "crawl.url"

    @staticmethod
    def _payload_extractor(event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract task payload from event.

        crawl.request events emitted via emit_event() have nested structure:
        {
          "event": "crawl.request",
          "data": {
            "url": "...",
            "source_id": 1,
            ...
          }
        }

        Args:
            event: Full event from Kafka

        Returns:
            Dict with fields to pass as kwargs to task
        """
        # Extract the data payload (events via emit_event have nested structure)
        data = event.get("data", {})
        return {
            "url": data.get("url"),
            "source_id": data.get("source_id"),
            "run_id": data.get("run_id"),
            "crawl_request_id": data.get("crawl_request_id"),
            "trace_id": data.get("trace_id"),
        }


def run_crawl_request_consumer() -> None:
    """Run the crawl request consumer.

    This subscribes to the crawl.request Kafka topic and routes events
    to the crawl_url task.
    """
    consumer = CrawlRequestConsumer()
    consumer.run()

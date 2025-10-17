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


class CrawlResultConsumer(GenericEventConsumer):
    """Consumer for crawl.result events.

    Routes crawl result events to the registered parse_crawled_content task
    (which will be implemented in the parse phase).
    """

    def __init__(self):
        """Initialize crawl result consumer."""
        super().__init__(
            topic="crawl.result",
            job_type_extractor=self._job_type_extractor,
            event_payload_extractor=self._payload_extractor,
            consumer_name="CrawlResultConsumer",
        )

    @staticmethod
    def _job_type_extractor(event: Dict[str, Any]) -> str:
        """Extract job_type from crawl result events.

        Args:
            event: Event dictionary from Kafka

        Returns:
            job_type string for routing to registered tasks
        """
        # crawl.result events should be routed to job_type="parse.content"
        # This will trigger the parse_crawled_content task
        return "parse.content"

    @staticmethod
    def _payload_extractor(event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract task payload from event.

        crawl.result events emitted via emit_event() have nested structure:
        {
          "event": "crawl.result",
          "data": {
            "artifact_id": 1,
            "blob_uri": "s3://...",
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
            "artifact_id": data.get("artifact_id"),
            "blob_uri": data.get("blob_uri"),
            "run_id": data.get("run_id"),
            "trace_id": data.get("trace_id"),
        }


def run_crawl_result_consumer() -> None:
    """Run the crawl result consumer.

    This subscribes to the crawl.result Kafka topic and routes events
    to the parse_crawled_content task (once implemented).

    Note: This is scaffolded for the future parse phase. The
    parse_crawled_content task currently raises NotImplementedError.
    """
    consumer = CrawlResultConsumer()
    consumer.run()

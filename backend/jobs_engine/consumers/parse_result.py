"""Consumer for parse result events (parse.result topic).

Listens to the parse.result topic and routes events to the next pipeline stage
(versioning) via the version.document job type.
"""

import logging
from typing import Any, Dict

from events.event_consumer import GenericEventConsumer

logger = logging.getLogger(__name__)


class ParseResultConsumer(GenericEventConsumer):
    """Consumer for parse.result events.

    Routes parse result events to the version_document task
    (next stage in pipeline).
    """

    def __init__(self):
        """Initialize parse result consumer."""
        super().__init__(
            topic="parse.result",
            job_type_extractor=self._job_type_extractor,
            event_payload_extractor=self._payload_extractor,
            consumer_name="ParseResultConsumer",
        )

    @staticmethod
    def _job_type_extractor(event: Dict[str, Any]) -> str:
        """Extract job_type from parse result events.

        Args:
            event: Event dictionary from Kafka

        Returns:
            job_type string for routing to registered tasks
        """
        # parse.result events route to versioning stage
        return "version.document"

    @staticmethod
    def _payload_extractor(event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract task payload from event.

        parse.result events have nested structure from emit_event():
        {
          "event": "parse.result",
          "data": {
            "doc_id": 1,
            "version_id": 2,
            "parsed_uri": "s3://...",
            "run_id": 5,
            "trace_id": "...",
            ...
          }
        }

        Args:
            event: Full event from Kafka

        Returns:
            Dict with fields to pass as kwargs to task
        """
        # Extract the data payload
        data = event.get("data", {})

        return {
            "doc_id": data.get("doc_id"),
            "version_id": data.get("version_id"),
            "parsed_uri": data.get("parsed_uri"),
            "run_id": data.get("run_id"),
            "trace_id": data.get("trace_id"),
        }


def run_parse_result_consumer() -> None:
    """Run the parse result consumer.

    This subscribes to the parse.result Kafka topic and routes events
    to the version_document task.
    """
    consumer = ParseResultConsumer()
    consumer.run()

"""Consumer for versioning result events (versioning.result topic).

Listens to the versioning.result topic and routes events to the next pipeline stage
(delivery) via the deliver.document job type.
"""

import logging
from typing import Any, Dict

from events.event_consumer import GenericEventConsumer

logger = logging.getLogger(__name__)


class VersioningResultConsumer(GenericEventConsumer):
    """Consumer for versioning.result events.

    Routes versioning result events to the deliver_document task
    (final stage in pipeline).
    """

    def __init__(self):
        """Initialize versioning result consumer."""
        super().__init__(
            topic="versioning.result",
            job_type_extractor=self._job_type_extractor,
            event_payload_extractor=self._payload_extractor,
            consumer_name="VersioningResultConsumer",
        )

    @staticmethod
    def _job_type_extractor(event: Dict[str, Any]) -> str:
        """Extract job_type from versioning result events.

        Args:
            event: Event dictionary from Kafka

        Returns:
            job_type string for routing to registered tasks
        """
        # versioning.result events route to delivery stage
        return "deliver.document"

    @staticmethod
    def _payload_extractor(event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract task payload from event.

        versioning.result events have nested structure from emit_event():
        {
          "event": "versioning.result",
          "data": {
            "doc_id": 1,
            "version_id": 2,
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
            "run_id": data.get("run_id"),
            "trace_id": data.get("trace_id"),
        }


def run_versioning_result_consumer() -> None:
    """Run the versioning result consumer.

    This subscribes to the versioning.result Kafka topic and routes events
    to the deliver_document task.
    """
    consumer = VersioningResultConsumer()
    consumer.run()

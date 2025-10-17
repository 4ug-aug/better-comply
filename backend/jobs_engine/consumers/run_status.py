"""Consumer for run status events (run.status topic).

Listens to the run.status topic and routes status update events
(started, completed, failed) to the update_run_status task.
"""

import logging
from typing import Any, Dict

from events.event_consumer import GenericEventConsumer

logger = logging.getLogger(__name__)


class RunStatusConsumer(GenericEventConsumer):
    """Consumer for run.status events.

    Routes run status events (started, completed, failed) to the
    registered update_run_status task.
    """

    def __init__(self):
        """Initialize run status consumer."""
        super().__init__(
            topic="run.status",
            job_type_extractor=self._job_type_extractor,
            event_payload_extractor=self._payload_extractor,
            consumer_name="RunStatusConsumer",
        )

    @staticmethod
    def _job_type_extractor(event: Dict[str, Any]) -> str:
        """Extract job_type from run status events.

        Args:
            event: Event dictionary from Kafka

        Returns:
            job_type string for routing to registered tasks
        """
        # All run status events route to the same job_type
        return "run.status.update"

    @staticmethod
    def _payload_extractor(event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract task payload from event.

        run.status events have nested structure from emit_event():
        {
          "event": "run.started|run.completed|run.failed",
          "data": {
            "run_id": 1,
            "trace_id": "...",
            "error_message": "..." (if failed),
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
        event_type = event.get("event", "")

        # Map event type to status
        status_map = {
            "run.started": "RUNNING",
            "run.completed": "COMPLETED",
            "run.failed": "FAILED",
        }
        status = status_map.get(event_type, "UNKNOWN")

        return {
            "run_id": data.get("run_id"),
            "status": status,
            "error_message": data.get("error_message"),
            "error_traceback": data.get("error_traceback"),
            "trace_id": data.get("trace_id"),
        }


def run_run_status_consumer() -> None:
    """Run the run status consumer.

    This subscribes to the run.status Kafka topic and routes events
    to the update_run_status task.
    """
    consumer = RunStatusConsumer()
    consumer.run()

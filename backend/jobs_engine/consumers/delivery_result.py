"""Consumer for delivery result events (delivery.result topic).

Listens to the delivery.result topic and emits run.completed events to mark
the run as successfully completed. This is the terminal event for the pipeline.
"""

import logging
from typing import Any, Dict

from events.event_consumer import GenericEventConsumer
from events.run_status_emitter import emit_run_completed

logger = logging.getLogger(__name__)


class DeliveryResultConsumer(GenericEventConsumer):
    """Consumer for delivery.result events.

    Routes delivery result events to emit run.completed status.
    This is the TERMINAL stage - when this consumer receives an event,
    it marks the entire run as COMPLETED.
    """

    def __init__(self):
        """Initialize delivery result consumer."""
        super().__init__(
            topic="delivery.result",
            job_type_extractor=self._job_type_extractor,
            event_payload_extractor=self._payload_extractor,
            consumer_name="DeliveryResultConsumer",
        )

    def run(self) -> None:
        """Override run to handle terminal event specially.

        Instead of dispatching to a task, directly emit run.completed.
        """
        logger.info(f"Starting {self.consumer_name} (topic={self.topic})")
        try:
            for message in self.consumer:
                try:
                    event_dict = self.deserialize(message.value)
                    logger.info(
                        f"{self.consumer_name} received event: {event_dict.get('event')}"
                    )

                    # Extract fields and emit run.completed
                    data = event_dict.get("data", {})
                    run_id = data.get("run_id")
                    trace_id = data.get("trace_id")
                    result = data.get("result", {})

                    logger.info(
                        f"{self.consumer_name}: Emitting run.completed for run_id={run_id}"
                    )
                    emit_run_completed(run_id, trace_id, result)

                except Exception as e:
                    logger.exception(f"Error processing delivery.result event: {e}")

        except KeyboardInterrupt:
            logger.info(f"{self.consumer_name} interrupted by user")
        except Exception as e:
            logger.exception(f"Fatal error in {self.consumer_name}: {e}")
        finally:
            self.consumer.close()

    @staticmethod
    def _job_type_extractor(event: Dict[str, Any]) -> str:
        """Extract job_type from delivery result events.

        Args:
            event: Event dictionary from Kafka

        Returns:
            job_type string (not used - we handle directly)
        """
        return "delivery.result.complete"

    @staticmethod
    def _payload_extractor(event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract task payload from event.

        delivery.result events have nested structure from emit_event():
        {
          "event": "delivery.result",
          "data": {
            "doc_id": 1,
            "version_id": 2,
            "run_id": 5,
            "trace_id": "...",
            "result": {...}
          }
        }

        Args:
            event: Full event from Kafka

        Returns:
            Dict with fields (not used - we handle directly)
        """
        data = event.get("data", {})
        return {
            "doc_id": data.get("doc_id"),
            "version_id": data.get("version_id"),
            "run_id": data.get("run_id"),
            "trace_id": data.get("trace_id"),
        }


def run_delivery_result_consumer() -> None:
    """Run the delivery result consumer.

    This subscribes to the delivery.result Kafka topic and emits run.completed
    events to mark the entire pipeline as successful.
    """
    consumer = DeliveryResultConsumer()
    consumer.run()

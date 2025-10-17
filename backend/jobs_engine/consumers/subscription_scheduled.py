"""Consumer for subscription scheduled events (subs.schedule topic).

Listens to the subs.schedule topic and routes events to the
handle_subscription_scheduled Celery task via routing system.
"""

import logging
from typing import Any, Dict

from events.event_consumer import GenericEventConsumer

logger = logging.getLogger(__name__)


class SubscriptionScheduledConsumer(GenericEventConsumer):
    """Consumer for subs.schedule events.

    Routes subscription scheduled events to the registered
    handle_subscription_scheduled task.
    """

    def __init__(self):
        """Initialize subscription scheduled consumer."""
        super().__init__(
            topic="subs.schedule",
            job_type_extractor=self._job_type_extractor,
            event_payload_extractor=self._payload_extractor,
            consumer_name="SubscriptionScheduledConsumer",
        )

    @staticmethod
    def _job_type_extractor(event: Dict[str, Any]) -> str:
        """Extract job_type from subscription scheduled events.

        Args:
            event: Event dictionary from Kafka

        Returns:
            job_type string for routing to registered tasks
        """
        # subs.schedule events should be routed to job_type="subscription.scheduled"
        return "subs.schedule"

    @staticmethod
    def _payload_extractor(event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract task payload from event.

        subs.schedule events have nested structure:
        {
          "event": "subs.schedule",
          "data": {
            "subscription_id": 1,
            "run_id": 5
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
            "subscription_id": data.get("subscription_id"),
            "run_id": data.get("run_id"),
        }


def run_subscription_scheduled_consumer() -> None:
    """Run the subscription scheduled consumer.

    This subscribes to the subs.schedule Kafka topic and routes events
    to the handle_subscription_scheduled task.
    """
    consumer = SubscriptionScheduledConsumer()
    consumer.run()

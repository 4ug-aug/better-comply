"""Consumer for subscription scheduled events (subs.schedule topic).

Listens to the subs.schedule topic and routes events to the
handle_subscription_scheduled Celery task via routing system.
"""

import logging
from typing import Any, Dict

from events.event_consumer import GenericEventConsumer

logger = logging.getLogger(__name__)


def subscription_scheduled_job_type_extractor(event: Dict[str, Any]) -> str:
    """Extract job_type from subscription scheduled events.

    Args:
        event: Event dictionary from Kafka

    Returns:
        job_type string for routing to registered tasks
    """
    # subs.schedule events should be routed to job_type="subscription.scheduled"
    return "subs.schedule"


class SubscriptionScheduledConsumer(GenericEventConsumer):
    """Consumer for subs.schedule events.

    Routes subscription scheduled events to the registered
    handle_subscription_scheduled task.
    """

    def __init__(self):
        """Initialize subscription scheduled consumer."""
        super().__init__(
            topic="events",
            job_type_extractor=subscription_scheduled_job_type_extractor,
            consumer_name="SubscriptionScheduledConsumer",
        )


def run_subscription_scheduled_consumer() -> None:
    """Run the subscription scheduled consumer.

    This subscribes to the subs.schedule Kafka topic and routes events
    to the handle_subscription_scheduled task.
    """
    consumer = SubscriptionScheduledConsumer()
    consumer.run()

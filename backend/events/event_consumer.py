"""Generic Kafka event consumer for dispatching events to Celery tasks.

This module provides a base class for consuming Kafka events and routing them
to registered Celery tasks via the routing system. Event type consumers should
inherit from GenericEventConsumer and provide a job_type_extractor function.
"""

import json
import logging
from typing import Callable, Any, Dict, Optional

from kafka import KafkaConsumer
from events.kafkaconfig import kafka_config
from jobs_engine.celery_app import app
from jobs_engine.routing import pick_task

logger = logging.getLogger(__name__)


class GenericEventConsumer:
    """Generic Kafka event consumer that dispatches to Celery tasks via routing.

    This consumer:
    1. Subscribes to a Kafka topic
    2. For each event message:
       - Parses JSON
       - Extracts job_type using a provided extractor function
       - Looks up task name using routing.pick_task(job_type)
       - Dispatches to Celery with event data as kwargs

    Subclasses should provide a job_type_extractor function that knows how to
    extract the job_type from the specific event format they're consuming.
    """

    def __init__(
        self,
        topic: str,
        job_type_extractor: Callable[[Dict[str, Any]], str],
        consumer_name: str = "EventConsumer",
    ):
        """Initialize the generic event consumer.

        Args:
            topic: Kafka topic to subscribe to
            job_type_extractor: Function that extracts job_type from event dict
            consumer_name: Name for logging purposes
        """
        self.topic = topic
        self.job_type_extractor = job_type_extractor
        self.consumer_name = consumer_name
        self.logger = logging.getLogger(f"{__name__}.{consumer_name}")

    def run(self) -> None:
        """Start consuming events from Kafka topic.

        This runs indefinitely until interrupted or an unrecoverable error occurs.
        """
        self.logger.info(f"Starting {self.consumer_name} for topic: {self.topic}")

        consumer = KafkaConsumer(**kafka_config)
        consumer.subscribe([self.topic])
        self.logger.info(f"Kafka consumer subscribed to topic: {self.topic}")

        try:
            for msg in consumer:
                self.logger.debug(f"Received message from {self.topic}: {msg}")
                try:
                    # Parse JSON event
                    event_dict = json.loads(msg.value.decode())
                except Exception as e:
                    self.logger.exception(
                        f"Failed to parse event JSON from {self.topic}; skipping: {e}"
                    )
                    continue

                try:
                    # Extract job_type using consumer-specific extractor
                    job_type = self.job_type_extractor(event_dict)
                    if not job_type:
                        self.logger.warning(
                            f"job_type_extractor returned None/empty for event: {event_dict}"
                        )
                        continue

                    # Resolve job_type to task name via routing
                    task_name = pick_task(job_type)
                    if not task_name:
                        self.logger.warning(
                            f"No task registered for job_type: {job_type}"
                        )
                        continue

                    self.logger.info(
                        f"Dispatching: job_type={job_type}, task={task_name}"
                    )

                    # Dispatch to Celery with event data as kwargs
                    try:
                        app.send_task(task_name, kwargs=event_dict, queue="jobs")
                        self.logger.info(f"Successfully dispatched task: {task_name}")
                    except Exception as e:
                        self.logger.exception(
                            f"Failed to dispatch task {task_name}: {e}"
                        )
                        continue

                except Exception as e:
                    self.logger.exception(
                        f"Unexpected error processing event from {self.topic}: {e}"
                    )
                    continue

        finally:
            consumer.close()
            self.logger.info(f"{self.consumer_name} stopped")

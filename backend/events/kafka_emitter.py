"""Kafka event emitter for publishing domain events.

This provides a simple interface to publish events directly to Kafka topics.
Celery workers consume these events and route them to appropriate handlers.

Usage:
    from events.kafka_emitter import emit_event
    
    emit_event("target.created", {"target_id": str(target.id), "email": target.email})
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional
from kafka import KafkaProducer

logger = logging.getLogger(__name__)

# Singleton producer instance
_producer: Optional[KafkaProducer] = None


def _get_producer() -> KafkaProducer:
    """Get or create the Kafka producer singleton."""
    global _producer
    
    if _producer is None:
        # Determine Kafka connection based on environment
        kafka_host = os.getenv("KAFKA_HOST", "kafka")
        kafka_port = os.getenv("KAFKA_PORT", "9093")
        
        bootstrap_servers = f"{kafka_host}:{kafka_port}"
        
        _producer = KafkaProducer(bootstrap_servers=[bootstrap_servers])
        logger.info("Kafka producer initialized with bootstrap_servers=%s", bootstrap_servers)
    
    return _producer


def emit_event(event_name: str, data: Dict[str, Any], topic: str = "events") -> bool:
    """Publish an event to Kafka.
    
    Events are published to the "events" topic and consumed by Celery workers
    which route them to appropriate task handlers.
    
    Args:
        event_name: Name of the event (e.g., "target.created")
        data: Event payload as a dictionary
        
    Returns:
        True if event was published successfully, False otherwise
        
    Example:
        emit_event("target.created", {
            "target_id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "name": "John Doe"
        })
    """
    try:
        producer = _get_producer()
        
        # Prepare message with event metadata
        message = {
            "event": event_name,
            "data": data,
        }
        message_bytes = json.dumps(message).encode("utf-8")
        
        # Produce to Kafka asynchronously
        producer.send(
            topic=topic,
            value=message_bytes,
            key=event_name.encode("utf-8")
        )
        
        # Trigger delivery of any buffered messages (non-blocking)
        producer.flush()
        
        logger.info("Event published to Kafka: %s → topic=%s", event_name, topic)
        return True
        
    except Exception:
        logger.exception("Failed to publish event to Kafka: %s", event_name)
        return False

def flush_events() -> None:
    """Flush any pending events. Useful for graceful shutdown."""
    global _producer
    if _producer is not None:
        _producer.flush(timeout=5.0)
        logger.info("Kafka producer flushed")


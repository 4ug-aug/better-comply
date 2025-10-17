"""Helper functions for emitting run status events.

Provides standardized event emission for task lifecycle tracking:
- run.started: Task begins execution
- run.completed: Task completes successfully
- run.failed: Task fails with exception
"""

import logging
from typing import Any, Dict, Optional

from events.kafka_emitter import emit_event

logger = logging.getLogger(__name__)


def emit_run_started(run_id: int, trace_id: str) -> bool:
    """Emit run.started event when a task begins.

    Args:
        run_id: The run ID
        trace_id: Trace ID for provenance tracking

    Returns:
        True if event was published successfully, False otherwise
    """
    payload = {
        "run_id": run_id,
        "trace_id": trace_id,
    }
    return emit_event("run.started", payload, topic="run.status")


def emit_run_completed(
    run_id: int, trace_id: str, result: Optional[Dict[str, Any]] = None
) -> bool:
    """Emit run.completed event when a task completes successfully.

    Args:
        run_id: The run ID
        trace_id: Trace ID for provenance tracking
        result: Optional result data from the task

    Returns:
        True if event was published successfully, False otherwise
    """
    payload = {
        "run_id": run_id,
        "trace_id": trace_id,
        "result": result,
    }
    return emit_event("run.completed", payload, topic="run.status")


def emit_run_failed(
    run_id: int,
    trace_id: str,
    error_message: str,
    error_traceback: Optional[str] = None,
) -> bool:
    """Emit run.failed event when a task fails.

    Args:
        run_id: The run ID
        trace_id: Trace ID for provenance tracking
        error_message: Human-readable error message
        error_traceback: Optional full traceback for debugging

    Returns:
        True if event was published successfully, False otherwise
    """
    payload = {
        "run_id": run_id,
        "trace_id": trace_id,
        "error_message": error_message,
        "error_traceback": error_traceback,
    }
    return emit_event("run.failed", payload, topic="run.status")

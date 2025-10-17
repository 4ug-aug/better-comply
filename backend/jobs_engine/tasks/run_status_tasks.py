"""Celery tasks for updating run status.

Handles run status lifecycle updates triggered by status events:
- RUNNING: Task has started
- COMPLETED: Task finished successfully
- FAILED: Task failed with error
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from jobs_engine.tasks.common import simple_task
from database.sync import SessionLocalSync
from models.run import Run, RunStatus

logger = logging.getLogger(__name__)


@simple_task(
    name="jobs_engine.tasks.run_status_tasks.update_run_status",
    queue="jobs",
    job_type="run.status.update",
)
def update_run_status(
    run_id: int,
    status: str,
    error_message: Optional[str] = None,
    error_traceback: Optional[str] = None,
    trace_id: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Update run status in database.

    This task is triggered by run status events (started, completed, failed)
    and updates the Run record accordingly.

    Args:
        run_id: The run ID to update
        status: New status (RUNNING, COMPLETED, FAILED)
        error_message: Error message if status is FAILED
        error_traceback: Full traceback if status is FAILED
        trace_id: Trace ID for provenance tracking
        **kwargs: Additional keyword arguments

    Returns:
        Dictionary with update status
    """
    logger.info(f"Updating run {run_id} to status {status} (trace_id={trace_id})")

    try:
        with SessionLocalSync() as db:
            run = db.get(Run, run_id)
            if not run:
                logger.warning(f"Run {run_id} not found")
                return {"status": "error", "message": f"Run {run_id} not found"}

            now = datetime.now(timezone.utc)

            # Map string status to RunStatus enum
            try:
                run_status = RunStatus[status]
            except KeyError:
                logger.warning(f"Invalid status: {status}")
                return {"status": "error", "message": f"Invalid status: {status}"}

            # Update run status
            run.status = run_status

            # Set ended_at for terminal states
            if status in ("COMPLETED", "FAILED"):
                run.ended_at = now

            # Store error if failed
            if status == "FAILED":
                error_detail = error_message or "Unknown error"
                if error_traceback:
                    error_detail = f"{error_detail}\n{error_traceback}"
                run.error = error_detail
                logger.error(f"Run {run_id} failed: {error_message}")

            db.commit()

            return {
                "status": "success",
                "run_id": run_id,
                "new_status": status,
                "trace_id": trace_id,
            }

    except Exception as e:
        logger.exception(f"Error updating run {run_id}: {e}")
        raise

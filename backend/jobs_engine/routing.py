from __future__ import annotations

from typing import Dict
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

# Dynamic registry mapping job types to Celery task names
JOB_TYPE_TO_TASK: Dict[str, str] = {}

def register_task_route(job_type: str, task_name: str) -> None:
    """Register a mapping from a domain job type to a Celery task name.

    This enables a simple, maintainable way to route incoming job events to
    Celery tasks without hard-coding static dictionaries in code.
    """
    JOB_TYPE_TO_TASK[job_type] = task_name
    logger.info(f"Registering task {task_name} with job type {job_type}")

def pick_task(job_type: str) -> str | None:
    """Resolve job type to Celery task name."""
    return JOB_TYPE_TO_TASK.get(job_type)

from typing import Any, Callable, Optional

from celery import Task
from jobs_engine.celery_app import app
from jobs_engine.routing import register_task_route
import logging

logger = logging.getLogger(__name__)

class BaseTask(Task):
    """Base task class for all celery tasks."""
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_kwargs = {"max_retries": 5}


def simple_task(
    *,
    name: str,
    queue: str = "default",
    job_type: Optional[str] = None,
    base: type[Task] = BaseTask,
    bind: bool = False,
    **task_kwargs: Any,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to define a Celery task and (optionally) register routing.

    Args:
        name: Celery task name (dotted path, e.g. "tasks.example.echo")
        queue: Queue name (default "default")
        job_type: If provided, register this domain job type to this task name
        base: Celery base task class (default BaseTask)
        bind: Whether to bind self (default False)
        **task_kwargs: Additional Celery @task kwargs

    Returns:
        The original function wrapped as a Celery task.
    """

    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        task = app.task(name=name, queue=queue, base=base, bind=bind, **task_kwargs)(func)
        logger.info(f"Registering task {name} with job type {job_type}")
        if job_type:
            register_task_route(job_type, name)
        return task

    return wrapper

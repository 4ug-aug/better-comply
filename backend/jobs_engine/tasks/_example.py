from __future__ import annotations
from typing import Any, Dict
from .common import simple_task


@simple_task(name="tasks.example.echo", queue="default", job_type="example.echo")
def echo(message: str, **kwargs: Any) -> Dict[str, Any]:
    return {"message": message, "kwargs": kwargs}


@simple_task(name="tasks.example.add", queue="default", job_type="example.add")
def add(a: int, b: int) -> int:
    return int(a) + int(b)


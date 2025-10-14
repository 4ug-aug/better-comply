"""Async runner utility for Celery tasks.

Provides a clean way to run async functions within Celery tasks
with proper error handling and logging.

Note: This utility is designed to work with Celery 5.4+ which has native async support.
"""

import asyncio
import logging
import threading
from typing import Callable, TypeVar, Awaitable

logger = logging.getLogger(__name__)

T = TypeVar('T')

# A single background event loop per worker process
_background_loop: asyncio.AbstractEventLoop | None = None
_background_thread: threading.Thread | None = None


def _ensure_background_loop() -> asyncio.AbstractEventLoop:
    global _background_loop, _background_thread
    if _background_loop is not None and _background_loop.is_running():
        return _background_loop

    loop = asyncio.new_event_loop()

    def _run_loop(loop_instance: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop_instance)
        loop_instance.run_forever()

    thread = threading.Thread(target=_run_loop, args=(loop,), name="celery-async-loop", daemon=True)
    thread.start()

    # Wait until loop is running
    while not loop.is_running():
        pass

    _background_loop = loop
    _background_thread = thread
    return loop


def run_async(async_func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
    """Run an async function in a Celery task with proper error handling.
    
    Schedules the coroutine onto a persistent background event loop to avoid
    cross-loop resource usage (e.g., asyncpg connections bound to a loop).
    """
    try:
        loop = _ensure_background_loop()
        coro = async_func(*args, **kwargs)
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result()
    except Exception as e:
        logger.error(f"Async function {async_func.__name__} failed: {e}")
        raise


async def run_async_in_context(async_func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
    """Run an async function within an existing async context.
    
    Use this when you're already in an async context and want to call another async function.
    """
    return await async_func(*args, **kwargs)

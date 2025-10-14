"""Database session helper for Celery tasks.

Provides proper session management for Celery tasks with automatic cleanup.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from database.connector import SessionLocal

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_task_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session for Celery tasks with proper cleanup.
    
    This function ensures that database connections are properly managed
    within the async context and handles connection pooling correctly.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        async with get_task_session() as session:
            # Use session here
            pass
    """
    session = SessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        await session.close()

"""Synchronous SQLAlchemy session for Celery tasks.

Celery workers and Beat run best with a synchronous DB client. This module
exposes a sync engine and `SessionLocalSync` bound to the same Postgres
database as the async API layer, but using the psycopg2 driver.
"""

import os
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "testdb")
POSTGRES_USER = os.getenv("POSTGRES_USER", "testuser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "testpassword")


DATABASE_URL_SYNC = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine_sync = create_engine(
    DATABASE_URL_SYNC,
    pool_pre_ping=True,
    future=True,
)

SessionLocalSync = sessionmaker(
    bind=engine_sync,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def get_sync_session() -> Iterator[Session]:
    """Context-style generator for a sync session.

    Example:
        with SessionLocalSync() as db:
            ...
    """
    db = SessionLocalSync()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()



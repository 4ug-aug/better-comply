from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base
import enum


class RunKind(str, enum.Enum):
    CRAWL = "crawl"
    PARSE = "parse"
    NORMALIZE = "normalize"
    SCHEDULE = "schedule"


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False, index=True)
    run_kind = Column(Enum(RunKind), nullable=False)
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    status = Column(Enum(RunStatus), default=RunStatus.PENDING)
    error = Column(Text, nullable=True)

    # Relationships
    subscription = relationship("Subscription", back_populates="runs")
    artifacts = relationship("Artifact", back_populates="run")

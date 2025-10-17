from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base
import enum


class RunKind(str, enum.Enum):
    CRAWL = "CRAWL"
    PARSE = "PARSE"
    NORMALIZE = "NORMALIZE"
    SCHEDULE = "SCHEDULE"


class RunStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    # subscription_id is nullable to allow orphaned runs when a subscription is deleted
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True, index=True)
    run_kind = Column(Enum(RunKind), nullable=False)
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    status = Column(Enum(RunStatus), default=RunStatus.PENDING)
    error = Column(Text, nullable=True)

    # Relationships
    subscription = relationship("Subscription", back_populates="runs")
    artifacts = relationship("Artifact", back_populates="run")

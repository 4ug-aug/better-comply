from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
from sqlalchemy.sql import func
from database.connection import Base
import enum


class ActorType(str, enum.Enum):
    SYSTEM = "system"
    USER = "user"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(Enum(ActorType), nullable=False)
    action = Column(String, nullable=False, index=True)
    subject_kind = Column(String, nullable=False, index=True)  # Type of entity being acted upon
    subject_id = Column(Integer, nullable=False, index=True)   # ID of the entity being acted upon
    at = Column(DateTime, server_default=func.now(), index=True)
    meta = Column(JSON, nullable=True)  # Additional metadata about the action

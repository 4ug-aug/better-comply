from sqlalchemy import Column, BigInteger, DateTime, Enum, String, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database.connection import Base
import enum

class OutboxStatus(str, enum.Enum):
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"

class Outbox(Base):
    __tablename__ = "outbox"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    event_type = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False)
    status = Column(Enum(OutboxStatus), default=OutboxStatus.PENDING.value, nullable=False, index=True)
    attempts = Column(Integer, default=0, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)



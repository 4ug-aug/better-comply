from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base
import enum


class DeliveryStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class DeliveryEvent(Base):
    __tablename__ = "delivery_events"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    version_id = Column(Integer, ForeignKey("document_versions.id"), nullable=False, index=True)
    subscriber_id = Column(String, nullable=False, index=True)  # External subscriber identifier
    attempt = Column(Integer, default=1)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    response_meta = Column(JSON, nullable=True)  # Response metadata from delivery
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    document = relationship("Document", back_populates="delivery_events")
    version = relationship("DocumentVersion", back_populates="delivery_events")

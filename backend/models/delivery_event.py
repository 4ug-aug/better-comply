"""DeliveryEvent model for tracking downstream document deliveries."""

import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base


class DeliveryStatus(str, enum.Enum):
    """Delivery status enum."""

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DeliveryEvent(Base):
    """Tracks downstream delivery events for document versions."""

    __tablename__ = "delivery_events"

    id = Column(Integer, primary_key=True, index=True)
    doc_version_id = Column(
        Integer, ForeignKey("document_versions.id"), nullable=False, index=True
    )
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING, index=True)
    artifact_type = Column(String, nullable=False)  # e.g., "parsed_document"
    delivery_uri = Column(String, nullable=True)  # Reference to delivered artifact
    error_message = Column(String, nullable=True)  # If FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    doc_version = relationship("DocumentVersion", backref="delivery_events")

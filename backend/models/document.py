from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    logical_key = Column(String, nullable=False, unique=True, index=True)  # Normalized source URL
    latest_version_id = Column(Integer, ForeignKey("document_versions.id"), nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    jurisdiction = Column(String, nullable=False, index=True)
    tags = Column(JSON, nullable=True)  # JSONB for flexible tagging
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    source = relationship("Source")
    latest_version = relationship("DocumentVersion", foreign_keys=[latest_version_id])
    versions = relationship("DocumentVersion", back_populates="document", foreign_keys="DocumentVersion.document_id")
    delivery_events = relationship("DeliveryEvent", back_populates="document")

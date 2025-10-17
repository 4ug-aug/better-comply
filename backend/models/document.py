from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base
from sqlalchemy import Index

class Document(Base):
    """Represents a unique document/regulation source."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    source_url = Column(String, nullable=False, unique=True, index=True)
    published_date = Column(String, nullable=True)  # ISO format or extracted date
    language = Column(String, default="en", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    source = relationship("Source", backref="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_document_source_url", "source_url"),
        Index("idx_document_source_id", "source_id"),
    )
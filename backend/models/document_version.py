from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base
from sqlalchemy import Index


class DocumentVersion(Base):
    """Represents a specific version of a document over time."""

    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    parsed_uri = Column(String, nullable=False)  # s3://artifacts/parsed/{doc_id}/{version_id}.json
    diff_uri = Column(String, nullable=True)  # s3://artifacts/diffs/{doc_id}/{version_id}.json
    content_hash = Column(String, nullable=False, index=True)  # SHA256 of parsed JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="versions")

    __table_args__ = (
        Index("idx_document_version_document_id", "document_id"),
        Index("idx_document_version_content_hash", "content_hash"),
    )
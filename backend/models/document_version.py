from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    artifact_id = Column(Integer, ForeignKey("artifacts.id"), nullable=False, index=True)
    text_hash = Column(String, nullable=False, index=True)  # Hash of processed text content
    text_uri = Column(String, nullable=False)  # MinIO URI for processed text
    created_at = Column(DateTime, server_default=func.now())
    prev_version_id = Column(Integer, ForeignKey("document_versions.id"), nullable=True)
    diff_uri = Column(String, nullable=True)  # MinIO URI for diff with previous version

    # Relationships
    document = relationship("Document", back_populates="versions", foreign_keys=[document_id])
    artifact = relationship("Artifact", back_populates="document_versions")
    prev_version = relationship("DocumentVersion", remote_side=[id])
    delivery_events = relationship("DeliveryEvent", back_populates="version")

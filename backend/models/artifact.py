from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    source_url = Column(String, nullable=False, index=True)
    content_type = Column(String, nullable=False)
    blob_uri = Column(String, nullable=False)  # MinIO URI
    fetch_hash = Column(String, nullable=False, index=True)  # Content hash for deduplication
    fetched_at = Column(DateTime, server_default=func.now())
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False, index=True)

    # Relationships
    run = relationship("Run", back_populates="artifacts")

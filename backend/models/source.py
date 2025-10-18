from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base
import enum


class SourceKind(str, enum.Enum):
    HTML = "html"
    API = "api"
    PDF = "pdf"


class RobotsMode(str, enum.Enum):
    ALLOW = "allow"
    DISALLOW = "disallow"
    CUSTOM = "custom"


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    kind = Column(Enum(SourceKind), nullable=False)
    base_url = Column(String, nullable=False)
    auth_ref = Column(String, nullable=True)  # Reference to auth configuration
    robots_mode = Column(Enum(RobotsMode), default=RobotsMode.ALLOW)
    rate_limit = Column(Integer, default=60)  # requests per minute
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    subscriptions = relationship("Subscription", back_populates="source")

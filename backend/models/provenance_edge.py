from sqlalchemy import Column, Integer, DateTime, JSON, Enum
from sqlalchemy.sql import func
from database.connection import Base
import enum


class ProvenanceKind(str, enum.Enum):
    FETCH = "fetch"
    PARSE = "parse"
    NORMALIZE = "normalize"
    DEDUPE = "dedupe"


class ProvenanceEdge(Base):
    __tablename__ = "provenance_edges"

    id = Column(Integer, primary_key=True, index=True)
    from_id = Column(Integer, nullable=False, index=True)  # Generic reference to any entity
    to_id = Column(Integer, nullable=False, index=True)    # Generic reference to any entity
    kind = Column(Enum(ProvenanceKind), nullable=False)
    at = Column(DateTime(timezone=True), server_default=func.now())
    prov_metadata = Column(JSON, nullable=True)  # W3C PROV-like metadata

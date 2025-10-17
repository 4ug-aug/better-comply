"""SQLAlchemy adapter for documents repository."""

from __future__ import annotations

import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload

from models.document import Document
from models.document_version import DocumentVersion
from documents.repositories.dto import (
    DocumentDTO,
    DocumentVersionDTO,
    DocumentWithVersionsDTO,
)
from documents.repositories.ports.documents import DocumentsRepository


class DocumentsAdapter(DocumentsRepository):
    """SQLAlchemy implementation of DocumentsRepository."""

    def __init__(self, db: Session):
        """Initialize adapter with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_all_documents(
        self, skip: int = 0, limit: int = 10
    ) -> List[DocumentDTO]:
        """Get all documents with pagination."""
        results = (
            self.db.query(Document)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._document_to_dto(doc) for doc in results]

    def get_document_by_id(self, doc_id: int) -> Optional[DocumentDTO]:
        """Get a single document by ID."""
        result = self.db.query(Document).filter(Document.id == doc_id).first()
        return self._document_to_dto(result) if result else None

    def get_document_by_url(self, source_url: str) -> Optional[DocumentDTO]:
        """Get a document by source URL (unique lookup)."""
        result = (
            self.db.query(Document).filter(Document.source_url == source_url).first()
        )
        return self._document_to_dto(result) if result else None

    def get_all_documents_with_versions(
        self, skip: int = 0, limit: int = 10
    ) -> List[DocumentWithVersionsDTO]:
        """Get all documents with their versions eagerly loaded."""
        results = (
            self.db.query(Document)
            .options(joinedload(Document.versions))
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._document_with_versions_to_dto(doc) for doc in results]

    def get_document_with_versions(
        self, doc_id: int
    ) -> Optional[DocumentWithVersionsDTO]:
        """Get a single document with all its versions."""
        result = (
            self.db.query(Document)
            .options(joinedload(Document.versions))
            .filter(Document.id == doc_id)
            .first()
        )
        return self._document_with_versions_to_dto(result) if result else None

    def get_documents_by_source_id(
        self, source_id: int, skip: int = 0, limit: int = 10
    ) -> List[DocumentDTO]:
        """Get documents filtered by source ID."""
        results = (
            self.db.query(Document)
            .filter(Document.source_id == source_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._document_to_dto(doc) for doc in results]

    def get_documents_by_language(
        self, language: str, skip: int = 0, limit: int = 10
    ) -> List[DocumentDTO]:
        """Get documents filtered by language."""
        results = (
            self.db.query(Document)
            .filter(Document.language == language)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._document_to_dto(doc) for doc in results]

    def get_parsed_document(self, version_id: int) -> Optional[Dict[str, Any]]:
        """Get parsed document content from MinIO by version ID.

        Args:
            version_id: Document version ID

        Returns:
            Parsed document JSON dict or None if not found

        Raises:
            ValueError: If MinIO fetch fails
        """
        # Fetch version record to get parsed_uri
        version = self.db.query(DocumentVersion).filter(
            DocumentVersion.id == version_id
        ).first()

        if not version:
            return None

        # Download from MinIO
        try:
            from jobs_engine.utils.minio_artifact_handler import download_artifact

            content_bytes = download_artifact(version.parsed_uri)
            parsed_doc = json.loads(content_bytes.decode('utf-8'))
            return parsed_doc

        except Exception as e:
            raise ValueError(f"Failed to fetch parsed document: {e}")

    # Helper methods

    @staticmethod
    def _document_to_dto(doc: Document) -> DocumentDTO:
        """Convert Document model to DTO."""
        return DocumentDTO(
            id=doc.id,
            source_id=doc.source_id,
            source_url=doc.source_url,
            published_date=doc.published_date,
            language=doc.language,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )

    @staticmethod
    def _version_to_dto(version: DocumentVersion) -> DocumentVersionDTO:
        """Convert DocumentVersion model to DTO."""
        return DocumentVersionDTO(
            id=version.id,
            document_id=version.document_id,
            parsed_uri=version.parsed_uri,
            diff_uri=version.diff_uri,
            content_hash=version.content_hash,
            created_at=version.created_at,
        )

    def _document_with_versions_to_dto(
        self, doc: Document
    ) -> DocumentWithVersionsDTO:
        """Convert Document with versions to DTO."""
        versions = sorted(
            [self._version_to_dto(v) for v in doc.versions],
            key=lambda v: v.created_at,
            reverse=True,
        )
        return DocumentWithVersionsDTO(
            document=self._document_to_dto(doc),
            versions=versions,
            version_count=len(versions),
        )

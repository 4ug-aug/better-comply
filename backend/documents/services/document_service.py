"""Document service for business logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from database.sync import SessionLocalSync
from documents.repositories.adapters.documents import DocumentsAdapter
from documents.repositories.dto import (
    DocumentDTO,
    DocumentWithVersionsDTO,
    AuditTrailEventDTO,
)


@dataclass
class DocumentService:
    """Service for document operations."""

    def get_all_documents(self, skip: int = 0, limit: int = 10) -> List[DocumentDTO]:
        """Get all documents with pagination.

        Args:
            skip: Number of documents to skip
            limit: Maximum documents to return

        Returns:
            List of DocumentDTO objects
        """
        with SessionLocalSync() as db:
            repo = DocumentsAdapter(db)
            return repo.get_all_documents(skip=skip, limit=limit)

    def get_document_by_id(self, doc_id: int) -> Optional[DocumentDTO]:
        """Get a single document by ID.

        Args:
            doc_id: Document ID

        Returns:
            DocumentDTO or None if not found
        """
        with SessionLocalSync() as db:
            repo = DocumentsAdapter(db)
            return repo.get_document_by_id(doc_id)

    def get_document_by_url(self, source_url: str) -> Optional[DocumentDTO]:
        """Get a document by source URL.

        Args:
            source_url: Source URL to search

        Returns:
            DocumentDTO or None if not found
        """
        with SessionLocalSync() as db:
            repo = DocumentsAdapter(db)
            return repo.get_document_by_url(source_url)

    def get_all_documents_with_versions(
        self, skip: int = 0, limit: int = 10
    ) -> List[DocumentWithVersionsDTO]:
        """Get all documents with their versions.

        Args:
            skip: Number of documents to skip
            limit: Maximum documents to return

        Returns:
            List of DocumentWithVersionsDTO objects
        """
        with SessionLocalSync() as db:
            repo = DocumentsAdapter(db)
            return repo.get_all_documents_with_versions(skip=skip, limit=limit)

    def get_document_with_versions(
        self, doc_id: int
    ) -> Optional[DocumentWithVersionsDTO]:
        """Get a single document with all its versions.

        Args:
            doc_id: Document ID

        Returns:
            DocumentWithVersionsDTO or None if not found
        """
        with SessionLocalSync() as db:
            repo = DocumentsAdapter(db)
            return repo.get_document_with_versions(doc_id)

    def get_documents_by_source_id(
        self, source_id: int, skip: int = 0, limit: int = 10
    ) -> List[DocumentDTO]:
        """Get documents filtered by source ID.

        Args:
            source_id: Source ID
            skip: Number to skip
            limit: Maximum to return

        Returns:
            List of DocumentDTO objects
        """
        with SessionLocalSync() as db:
            repo = DocumentsAdapter(db)
            return repo.get_documents_by_source_id(
                source_id=source_id, skip=skip, limit=limit
            )

    def get_documents_by_language(
        self, language: str, skip: int = 0, limit: int = 10
    ) -> List[DocumentDTO]:
        """Get documents filtered by language.

        Args:
            language: Language code (e.g., 'en')
            skip: Number to skip
            limit: Maximum to return

        Returns:
            List of DocumentDTO objects
        """
        with SessionLocalSync() as db:
            repo = DocumentsAdapter(db)
            return repo.get_documents_by_language(
                language=language, skip=skip, limit=limit
            )

    def get_parsed_document(self, version_id: int) -> Optional[Dict[str, Any]]:
        """Get parsed document content from MinIO by version ID.

        Args:
            version_id: Document version ID

        Returns:
            Parsed document JSON dict or None if not found

        Raises:
            ValueError: If MinIO fetch fails
        """
        with SessionLocalSync() as db:
            repo = DocumentsAdapter(db)
            return repo.get_parsed_document(version_id)

    def get_version_audit_trail(self, version_id: int) -> List[AuditTrailEventDTO]:
        """Get audit trail for a specific document version.

        Traces the processing chain for a version using the direct run_id FK.

        Args:
            version_id: Document version ID

        Returns:
            List of AuditTrailEventDTO objects sorted by timestamp
        """
        with SessionLocalSync() as db:
            repo = DocumentsAdapter(db)
            return repo.get_version_audit_trail(version_id)

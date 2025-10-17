"""Documents repository port (interface)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from documents.repositories.dto import (
    DocumentDTO,
    DocumentVersionDTO,
    DocumentWithVersionsDTO,
)


class DocumentsRepository(ABC):
    """Abstract repository interface for documents."""

    @abstractmethod
    def get_all_documents(
        self, skip: int = 0, limit: int = 10
    ) -> List[DocumentDTO]:
        """Get all documents with pagination.

        Args:
            skip: Number of documents to skip
            limit: Maximum documents to return

        Returns:
            List of DocumentDTO objects
        """
        pass

    @abstractmethod
    def get_document_by_id(self, doc_id: int) -> Optional[DocumentDTO]:
        """Get a single document by ID.

        Args:
            doc_id: Document ID

        Returns:
            DocumentDTO or None if not found
        """
        pass

    @abstractmethod
    def get_document_by_url(self, source_url: str) -> Optional[DocumentDTO]:
        """Get a document by source URL (unique lookup).

        Args:
            source_url: Source URL to search

        Returns:
            DocumentDTO or None if not found
        """
        pass

    @abstractmethod
    def get_all_documents_with_versions(
        self, skip: int = 0, limit: int = 10
    ) -> List[DocumentWithVersionsDTO]:
        """Get all documents with their versions eagerly loaded.

        Args:
            skip: Number of documents to skip
            limit: Maximum documents to return

        Returns:
            List of DocumentWithVersionsDTO objects
        """
        pass

    @abstractmethod
    def get_document_with_versions(
        self, doc_id: int
    ) -> Optional[DocumentWithVersionsDTO]:
        """Get a single document with all its versions.

        Args:
            doc_id: Document ID

        Returns:
            DocumentWithVersionsDTO or None if not found
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

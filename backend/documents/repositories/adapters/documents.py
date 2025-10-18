"""SQLAlchemy adapter for documents repository."""

from __future__ import annotations

import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone

from models.document import Document
from models.document_version import DocumentVersion
from models.outbox import Outbox
from models.run import Run
from models.artifact import Artifact
from documents.repositories.dto import (
    DocumentDTO,
    DocumentVersionDTO,
    DocumentWithVersionsDTO,
    AuditTrailEventDTO,
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

    def get_version_audit_trail(self, version_id: int) -> List[AuditTrailEventDTO]:
        """Get audit trail for a specific document version.

        Returns all steps in the processing pipeline for a version:
        Outbox (scheduled) → Run (executed) → Artifact (fetched) → 
        DocumentVersion (parsed) → DeliveryEvent (delivered)

        Args:
            version_id: Document version ID

        Returns:
            List of AuditTrailEventDTO objects, one per pipeline step, sorted by timestamp
        """
        from models.delivery_event import DeliveryEvent

        events: List[AuditTrailEventDTO] = []

        # Fetch the DocumentVersion
        version = (
            self.db.query(DocumentVersion)
            .filter(DocumentVersion.id == version_id)
            .first()
        )

        if not version or not version.run_id:
            return events

        # Fetch the Run using the FK
        run = self.db.query(Run).filter(Run.id == version.run_id).first()
        if not run:
            return events

        # Fetch the single Artifact for this Run
        artifact = (
            self.db.query(Artifact)
            .filter(Artifact.run_id == version.run_id)
            .first()
        )

        # Fetch the Outbox event for this Run using JSONB query
        outbox_event = (
            self.db.query(Outbox)
            .filter(Outbox.payload.contains({'run_id': version.run_id}))
            .first()
        )

        # Step 1: Outbox Event (scheduled the run)
        if outbox_event:
            event = AuditTrailEventDTO(
                event_type="outbox",
                event_id=outbox_event.id,
                timestamp=outbox_event.created_at,
                status=outbox_event.status.value if outbox_event.status else "UNKNOWN",
                run_id=version.run_id,
                run_kind=run.run_kind.value if run.run_kind else None,
                artifact_ids=[],
                artifact_uris=[],
                version_id=None,
                parsed_uri=None,
                diff_uri=None,
                content_hash=None,
                error=None,
            )
            events.append(event)

        # Step 2: Run Execution
        event = AuditTrailEventDTO(
            event_type="run",
            event_id=run.id,
            timestamp=run.started_at,
            status=run.status.value if run.status else "UNKNOWN",
            run_id=version.run_id,
            run_kind=run.run_kind.value if run.run_kind else None,
            artifact_ids=[],
            artifact_uris=[],
            version_id=None,
            parsed_uri=None,
            diff_uri=None,
            content_hash=None,
            error=run.error if run.status and run.status.value == "FAILED" else None,
        )
        events.append(event)

        # Step 3: Artifact Created (raw content fetched)
        if artifact:
            event = AuditTrailEventDTO(
                event_type="artifact",
                event_id=artifact.id,
                timestamp=artifact.fetched_at,
                status="COMPLETED",
                run_id=version.run_id,
                run_kind=run.run_kind.value if run.run_kind else None,
                artifact_ids=[artifact.id],
                artifact_uris=[artifact.blob_uri],
                version_id=None,
                parsed_uri=None,
                diff_uri=None,
                content_hash=artifact.fetch_hash,
                error=None,
            )
            events.append(event)

        # Step 4: DocumentVersion Created (parsed content)
        event = AuditTrailEventDTO(
            event_type="document_version",
            event_id=version.id,
            timestamp=version.created_at,
            status="COMPLETED",
            run_id=version.run_id,
            run_kind=run.run_kind.value if run.run_kind else None,
            artifact_ids=[artifact.id] if artifact else [],
            artifact_uris=[artifact.blob_uri] if artifact else [],
            version_id=version.id,
            parsed_uri=version.parsed_uri,
            diff_uri=version.diff_uri,
            content_hash=version.content_hash,
            error=None,
        )
        events.append(event)

        # Step 5: DeliveryEvent (downstream delivery)
        delivery_events = (
            self.db.query(DeliveryEvent)
            .filter(DeliveryEvent.doc_version_id == version.id)
            .all()
        )

        for delivery in delivery_events:
            event = AuditTrailEventDTO(
                event_type="delivery",
                event_id=delivery.id,
                timestamp=delivery.created_at,
                status=delivery.status.value if delivery.status else "UNKNOWN",
                run_id=version.run_id,
                run_kind=run.run_kind.value if run.run_kind else None,
                artifact_ids=[artifact.id] if artifact else [],
                artifact_uris=[artifact.blob_uri] if artifact else [],
                version_id=version.id,
                parsed_uri=version.parsed_uri,
                diff_uri=version.diff_uri,
                content_hash=version.content_hash,
                error=delivery.error_message if delivery.status and delivery.status.value == "FAILED" else None,
            )
            events.append(event)

        # Sort events by timestamp
        events.sort(key=lambda x: self._ensure_utc_datetime(x.timestamp), reverse=True)

        return events

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

    @staticmethod
    def _ensure_utc_datetime(dt: Optional[datetime]) -> Optional[datetime]:
        """Ensure a datetime object is timezone-aware (UTC).
        
        Args:
            dt: Optional datetime object
            
        Returns:
            Timezone-aware datetime in UTC, or None if input is None
        """
        if dt is None:
            return None
        
        if dt.tzinfo is None:
            # Naive datetime - assume UTC
            return dt.replace(tzinfo=timezone.utc)
        
        # Already aware, ensure it's UTC
        return dt.astimezone(timezone.utc)

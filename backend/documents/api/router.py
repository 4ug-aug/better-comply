"""Document API routes."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException

from documents.api.schemas import (
    DocumentOut,
    DocumentDetailOut,
    DocumentListResponse,
    DocumentDetailListResponse,
    ParsedDocumentOut,
)
from documents.services.document_service import DocumentService


def get_service() -> DocumentService:
    """Get document service instance."""
    return DocumentService()


router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    source_id: Optional[int] = Query(None),
    language: Optional[str] = Query(None),
    service: DocumentService = Depends(get_service),
) -> DocumentListResponse:
    """List all documents with optional filtering.

    Args:
        skip: Number of documents to skip
        limit: Maximum documents to return
        source_id: Filter by source ID
        language: Filter by language code

    Returns:
        DocumentListResponse with paginated documents
    """
    if source_id is not None:
        items = service.get_documents_by_source_id(
            source_id=source_id, skip=skip, limit=limit
        )
    elif language is not None:
        items = service.get_documents_by_language(
            language=language, skip=skip, limit=limit
        )
    else:
        items = service.get_all_documents(skip=skip, limit=limit)

    # Convert DTOs to response models
    response_items = [
        DocumentOut(
            id=item.id,
            source_id=item.source_id,
            source_url=item.source_url,
            published_date=item.published_date,
            language=item.language,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in items
    ]

    return DocumentListResponse(
        items=response_items, total=len(response_items), skip=skip, limit=limit
    )


@router.get("/with-versions", response_model=DocumentDetailListResponse)
def list_documents_with_versions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: DocumentService = Depends(get_service),
) -> DocumentDetailListResponse:
    """List all documents with their versions.

    Args:
        skip: Number of documents to skip
        limit: Maximum documents to return

    Returns:
        DocumentDetailListResponse with paginated documents and versions
    """
    items = service.get_all_documents_with_versions(skip=skip, limit=limit)

    # Convert DTOs to response models
    response_items = [
        DocumentDetailOut(
            id=doc_with_versions.document.id,
            source_id=doc_with_versions.document.source_id,
            source_url=doc_with_versions.document.source_url,
            published_date=doc_with_versions.document.published_date,
            language=doc_with_versions.document.language,
            created_at=doc_with_versions.document.created_at,
            updated_at=doc_with_versions.document.updated_at,
            versions=[
                {
                    "id": v.id,
                    "document_id": v.document_id,
                    "parsed_uri": v.parsed_uri,
                    "diff_uri": v.diff_uri,
                    "content_hash": v.content_hash,
                    "created_at": v.created_at,
                }
                for v in doc_with_versions.versions
            ],
            version_count=doc_with_versions.version_count,
        )
        for doc_with_versions in items
    ]

    return DocumentDetailListResponse(
        items=response_items, total=len(response_items), skip=skip, limit=limit
    )


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(
    doc_id: int, service: DocumentService = Depends(get_service)
) -> DocumentOut:
    """Get a single document by ID.

    Args:
        doc_id: Document ID

    Returns:
        DocumentOut response

    Raises:
        HTTPException: 404 if document not found
    """
    result = service.get_document_by_id(doc_id)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentOut(
        id=result.id,
        source_id=result.source_id,
        source_url=result.source_url,
        published_date=result.published_date,
        language=result.language,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.get("/{doc_id}/versions", response_model=DocumentDetailOut)
def get_document_with_versions(
    doc_id: int, service: DocumentService = Depends(get_service)
) -> DocumentDetailOut:
    """Get a document with all its versions.

    Args:
        doc_id: Document ID

    Returns:
        DocumentDetailOut response with all versions

    Raises:
        HTTPException: 404 if document not found
    """
    result = service.get_document_with_versions(doc_id)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentDetailOut(
        id=result.document.id,
        source_id=result.document.source_id,
        source_url=result.document.source_url,
        published_date=result.document.published_date,
        language=result.document.language,
        created_at=result.document.created_at,
        updated_at=result.document.updated_at,
        versions=[
            {
                "id": v.id,
                "document_id": v.document_id,
                "parsed_uri": v.parsed_uri,
                "diff_uri": v.diff_uri,
                "content_hash": v.content_hash,
                "created_at": v.created_at,
            }
            for v in result.versions
        ],
        version_count=result.version_count,
    )


@router.get("/by-url/{source_url}", response_model=DocumentOut)
def get_document_by_url(
    source_url: str, service: DocumentService = Depends(get_service)
) -> DocumentOut:
    """Get a document by source URL.

    Args:
        source_url: Source URL to search

    Returns:
        DocumentOut response

    Raises:
        HTTPException: 404 if document not found
    """
    result = service.get_document_by_url(source_url)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentOut(
        id=result.id,
        source_id=result.source_id,
        source_url=result.source_url,
        published_date=result.published_date,
        language=result.language,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.get("/{doc_id}/versions/{version_id}/parsed", response_model=ParsedDocumentOut)
def get_parsed_document(
    doc_id: int, version_id: int, service: DocumentService = Depends(get_service)
) -> ParsedDocumentOut:
    """Get parsed document content from MinIO by version ID.

    Args:
        doc_id: Document ID (for route validation)
        version_id: Document version ID

    Returns:
        ParsedDocumentOut with full parsed content

    Raises:
        HTTPException: 404 if document version not found
        HTTPException: 500 if MinIO fetch fails
    """
    try:
        result = service.get_parsed_document(version_id)
        if not result:
            raise HTTPException(status_code=404, detail="Document version not found")

        return ParsedDocumentOut(**result)

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch parsed document: {str(e)}"
        )

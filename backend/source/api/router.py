from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List

from source.api.schemas import (
    SourceOut,
    SourceDetailOut,
    CreateSourceRequest,
    UpdateSourceRequest,
    SourceResponse,
)
from source.services.source_service import SourceService


def get_service() -> SourceService:
    return SourceService()


router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/", response_model=List[SourceOut])
def list_sources(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    svc: SourceService = Depends(get_service),
) -> List[SourceOut]:
    """List all sources with pagination."""
    sources = svc.list_sources(limit=limit, offset=offset)
    return [SourceOut(**source) for source in sources]


@router.get("/{source_id}", response_model=SourceDetailOut)
def get_source(
    source_id: int,
    svc: SourceService = Depends(get_service),
) -> SourceDetailOut:
    """Get a specific source by ID."""
    source = svc.get_source(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with id {source_id} not found"
        )
    return SourceDetailOut(**source)


@router.post("/", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def create_source(
    data: CreateSourceRequest,
    svc: SourceService = Depends(get_service),
) -> SourceResponse:
    """Create a new source."""
    source = svc.create_source(data.dict())
    return SourceResponse(**source)


@router.put("/{source_id}", response_model=SourceResponse)
def update_source(
    source_id: int,
    data: UpdateSourceRequest,
    svc: SourceService = Depends(get_service),
) -> SourceResponse:
    """Update an existing source."""
    # Filter out None values for partial updates
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )
    
    source = svc.update_source(source_id, update_data)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with id {source_id} not found"
        )
    return SourceResponse(**source)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    source_id: int,
    svc: SourceService = Depends(get_service),
) -> None:
    """Delete a source."""
    success = svc.delete_source(source_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with id {source_id} not found"
        )

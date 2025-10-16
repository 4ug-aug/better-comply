from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from typing import Optional, List

from scheduling.api.schemas import (
    BatchRequest,
    TickResult,
    ComputeNextResult,
    DispatchResult,
    SubscriptionOut,
    RunOut,
    OutboxOut,
)
from scheduling.services.scheduling_service import SchedulingService


def get_service() -> SchedulingService:
    return SchedulingService()


router = APIRouter(prefix="/scheduling", tags=["scheduling"])


@router.post("/tick", response_model=TickResult)
def tick(data: BatchRequest, svc: SchedulingService = Depends(get_service)) -> TickResult:
    processed = svc.tick(batch_size=data.batch_size)
    return TickResult(processed=processed)


@router.post("/compute-next", response_model=ComputeNextResult)
def compute_next(data: BatchRequest, svc: SchedulingService = Depends(get_service)) -> ComputeNextResult:
    updated = svc.compute_next(batch_size=data.batch_size)
    return ComputeNextResult(updated=updated)


@router.post("/outbox/dispatch", response_model=DispatchResult)
def dispatch_outbox(data: BatchRequest, svc: SchedulingService = Depends(get_service)) -> DispatchResult:
    published = svc.dispatch_outbox(batch_size=data.batch_size)
    return DispatchResult(published=published)


@router.get("/subscriptions", response_model=List[SubscriptionOut])
def list_subscriptions(
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    svc: SchedulingService = Depends(get_service),
) -> List[SubscriptionOut]:
    rows = svc.list_subscriptions(status=status, limit=limit, offset=offset)
    return [SubscriptionOut(**r) for r in rows]


@router.get("/runs", response_model=List[RunOut])
def list_runs(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    svc: SchedulingService = Depends(get_service),
) -> List[RunOut]:
    rows = svc.list_runs(limit=limit, offset=offset)
    return [RunOut(**r) for r in rows]


@router.get("/outbox", response_model=List[OutboxOut])
def list_outbox(
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    svc: SchedulingService = Depends(get_service),
) -> List[OutboxOut]:
    rows = svc.list_outbox(status=status, limit=limit, offset=offset)
    return [OutboxOut(**r) for r in rows]



from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import StreamingResponse
import json
import asyncio

from observability.services.observability_service import ObservabilityService
from auth.services import get_current_user_from_token


router = APIRouter(prefix="/observability", tags=["observability"])


def get_service() -> ObservabilityService:
    return ObservabilityService()


@router.get("/stream")
async def stream_observability(token: str = Query(..., description="Authentication token")):
    """Stream observability data (outbox and runs) via Server-Sent Events.
    
    Sends initial snapshot, then periodic updates every 3 seconds.
    Requires authentication token as query parameter since EventSource doesn't support custom headers.
    """
    # Validate token
    user = await get_current_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    
    svc = get_service()
    
    async def event_generator():
        try:
            while True:
                # Get current snapshot of observability data
                data = svc.get_observability_snapshot(limit=50)
                
                # Format as SSE
                event_data = json.dumps(data)
                yield f"data: {event_data}\n\n"
                
                # Wait before next update
                await asyncio.sleep(3)
        except asyncio.CancelledError:
            # Client disconnected
            pass
        except Exception as e:
            # Log error and send error event
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

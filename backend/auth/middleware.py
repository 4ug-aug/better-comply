from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Optional
import logging

from auth.services import get_current_user_from_token
from config.settings import settings

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware that protects all endpoints by default.
    Exclude specific paths from authentication by adding them to excluded_paths.
    """
    
    def __init__(self, app, excluded_paths: Optional[List[str]] = None):
        super().__init__(app)
        # Default excluded paths (public endpoints)
        self.excluded_paths = excluded_paths or [
            "/",
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/auth/register",
            "/auth/token",
            "/auth/refresh",
            "/auth/verify-email",
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Extract token from Authorization header
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header missing"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            # Extract token from "Bearer <token>" format
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authorization scheme")
            
            # Validate token and get user
            user = await get_current_user_from_token(token)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Add user to request state for use in route handlers
            request.state.current_user = user
            
        except ValueError as e:
            logger.warning(f"Invalid authorization header: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header format"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
                headers=e.headers or {},
            )
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication failed"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Continue to the next middleware/route handler
        return await call_next(request)

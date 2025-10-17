from fastapi import FastAPI, Request
import os
import logging
from auth.routes import router as auth_router
from scheduling.api.router import router as scheduling_router
from source.api.router import router as source_router
from documents.api.router import router as documents_router
from observability.api.router import router as observability_router
from auth.middleware import AuthMiddleware
from models.user import User

# Basic logging configuration
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)
logger.info("Logging initialized with level %s", log_level)

app = FastAPI(title="Better Comply API", version="1.0.0")

# Add authentication middleware to protect all endpoints by default
# Exclude observability stream from auth middleware since it authenticates via query param
app.add_middleware(
    AuthMiddleware,
    excluded_paths=[
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/auth/register",
        "/auth/token",
        "/auth/refresh",
        "/auth/verify-email",
        "/observability/stream",
    ]
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(scheduling_router)
app.include_router(source_router)
app.include_router(documents_router)
app.include_router(observability_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/protected")
async def protected_endpoint(request: Request):
    # Get user from middleware (already authenticated)
    current_user: User = request.state.current_user
    return {
        "message": "You are authenticated",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
        }
    }


@app.get("/admin")
async def admin_endpoint(request: Request):
    # Get user from middleware and check admin status
    current_user: User = request.state.current_user
    if not current_user.is_admin:
        return {"message": "Access denied. Admin privileges required."}
    
    return {
        "message": "Admin access granted",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "is_admin": current_user.is_admin,
        }
    }
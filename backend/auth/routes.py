from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.services import (
    hash_password,
    create_access_token,
    create_refresh_token,
    authenticate_user,
    decode_token,
    token_expired
)
from auth.validators import CreateUserRequest, RefreshTokenRequest, Token
from config.settings import settings
from database.connection import get_db
from models.user import User

router = APIRouter()

@router.post("/register", status_code=201)
async def register_user(
    create_user_request: CreateUserRequest,
    db: AsyncSession = Depends(get_db),
):
    # Check if username or email exists
    existing_user_by_username = await db.execute(
        select(User).where(User.username == create_user_request.username)
    )
    if existing_user_by_username.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken.")

    existing_user_by_email = await db.execute(
        select(User).where(User.email == create_user_request.email)
    )
    if existing_user_by_email.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already taken.")

    hashed_password = hash_password(create_user_request.password)

    user = User(
        username=create_user_request.username,
        email=create_user_request.email,
        hashed_password=hashed_password,
    )
    db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="User already exists.")

    return {"message": "User registered successfully"}

@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    if not user.is_verified:
        # If email verification is not yet implemented, allow login; otherwise enforce.
        pass

    access_token = create_access_token(
        user.username,
        user.id,
        timedelta(days=settings.ACCESS_TOKEN_EXPIRATION_DAYS)
    )
    refresh_token = create_refresh_token(
        user.username,
        user.id,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRATION_DAYS)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token_request: RefreshTokenRequest):
    token = refresh_token_request.refresh_token

    if token_expired(token):
        raise HTTPException(status_code=401, detail="Refresh token expired.")

    user_data = decode_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token.")

    username = user_data.get("sub")
    user_id = user_data.get("id")

    if not username or not user_id:
        raise HTTPException(status_code=401, detail="Invalid token.")

    # Generate new tokens
    access_token = create_access_token(username, user_id, timedelta(days=settings.ACCESS_TOKEN_EXPIRATION_DAYS))
    refresh_token = create_refresh_token(username, user_id, timedelta(days=settings.REFRESH_TOKEN_EXPIRATION_DAYS))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/verify-email")
async def verify_email(
    db: AsyncSession = Depends(get_db), 
    token: str = Query(..., description="The verification token")
):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    try:
        username = payload["sub"]

        user = await db.execute(select(User).where(User.username == username))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return RedirectResponse(f"{settings.FRONTEND_URL}/login?detail=already_verified")

        user.is_verified = True
        await db.commit()

        return RedirectResponse(f"{settings.FRONTEND_URL}/login?detail=email_verified")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid verification token")


@router.get("/me")
async def read_users_me(request: Request):
    current_user: User = request.state.current_user
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_verified": current_user.is_verified,
        "is_admin": current_user.is_admin,
    }
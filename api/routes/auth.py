
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models import User, LoginSession

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

password_hash = PasswordHash.recommended()

COOKIE_NAME = "paypulse_session"
SESSION_DAYS = 7


class SignupRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    business_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    full_name: str
    business_name: str
    email: EmailStr

    model_config = {"from_attributes": True}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_current_session(
    request: Request,
    db: Session,
):
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    session = db.scalar(
        select(LoginSession).where(
            LoginSession.token_hash == hash_token(token)
        )
    )

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid session",
        )

    expires_at = session.expires_at

    # Handle PostgreSQL datetime values consistently
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="Session expired",
        )

    return session


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    data: SignupRequest,
    db: Session = Depends(get_db),
):
    email = data.email.strip().lower()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    user = User(
        full_name=data.full_name.strip(),
        business_name=data.business_name.strip(),
        email=email,
        password_hash=password_hash.hash(data.password),
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    return user


@router.post("/login", response_model=UserResponse)
def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    email = data.email.strip().lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not password_hash.verify(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    token = secrets.token_urlsafe(32)

    session = LoginSession(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(days=SESSION_DAYS)
        ),
    )

    db.add(session)
    db.commit()

    # Set COOKIE_SECURE=true on Render (HTTPS).
    # For localhost HTTP testing, leave it false.
    secure_cookie = (
        os.getenv("COOKIE_SECURE", "false").lower()
        == "true"
    )

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=secure_cookie,
        samesite=(
            "none" if secure_cookie else "lax"
        ),
        max_age=SESSION_DAYS * 24 * 60 * 60,
        path="/",
    )

    return user


@router.get("/me", response_model=UserResponse)
def me(
    request: Request,
    db: Session = Depends(get_db),
):
    session = get_current_session(request, db)

    user = db.get(User, session.user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    token = request.cookies.get(COOKIE_NAME)

    if token:
        session = db.scalar(
            select(LoginSession).where(
                LoginSession.token_hash == hash_token(token)
            )
        )

        if session:
            db.delete(session)
            db.commit()

    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
    )

    return {"message": "Logged out successfully"}

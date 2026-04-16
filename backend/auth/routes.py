"""
ACDRIP+ Authentication Routes
User registration, login, and profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from database import get_db
from models import User
from auth.utils import hash_password, verify_password, create_access_token, get_current_user
import re

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ── Request/Response Schemas ──────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email address")
        return v.lower().strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: str


# ── Routes ──────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    # Check if email already exists
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create user
    user = User(
        name=req.name,
        email=req.email,
        password_hash=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate token
    token = create_access_token(data={"sub": user.id, "email": user.email})

    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    token = create_access_token(data={"sub": user.id, "email": user.email})

    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
    )


@router.get("/me")
def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "created_at": str(current_user.created_at),
        "is_active": current_user.is_active,
    }

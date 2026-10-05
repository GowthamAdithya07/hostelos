import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .database import get_db
from . import models

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "recoverease-secret-jwt-token-key-2025-super-secure-production-ready")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

security = HTTPBearer(auto_error=False)


# ===================== PASSWORD HASHING =====================

def get_password_hash(password: str) -> str:
    """Hash a password using direct bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


# ===================== JWT TOKENS =====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a short-lived access JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a longer-lived refresh JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def find_user_by_id_and_role(db: Session, user_id: int, role: Optional[str] = None):
    """Resolve an account across the 10-table schema: admins, authorities, students."""
    if role in [models.UserRole.INSTITUTE_HEAD.value, models.UserRole.ADMIN.value]:
        admin = db.query(models.Admin).filter(models.Admin.id == user_id).first()
        if admin:
            return admin
    elif role == models.UserRole.WARDEN.value:
        auth = db.query(models.Authority).filter(models.Authority.id == user_id).first()
        if auth:
            return auth
    elif role == models.UserRole.STUDENT.value:
        stud = db.query(models.Student).filter(models.Student.id == user_id).first()
        if stud:
            return stud

    # Fallback search if role was not specified
    stud = db.query(models.Student).filter(models.Student.id == user_id).first()
    if stud:
        return stud
    admin = db.query(models.Admin).filter(models.Admin.id == user_id).first()
    if admin:
        return admin
    auth = db.query(models.Authority).filter(models.Authority.id == user_id).first()
    if auth:
        return auth
    return None


# ===================== AUTH DEPENDENCIES =====================

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    """Authenticate the current user using the Bearer token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type for authorization",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    role = payload.get("role")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = find_user_by_id_and_role(db, int(user_id), role)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    """Return user if valid Bearer token provided, else None without raising 401."""
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        role = payload.get("role")
        if not user_id:
            return None
        return find_user_by_id_and_role(db, int(user_id), role)
    except Exception:
        return None


def get_current_warden_or_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """Ensure the authenticated user is either a WARDEN or an INSTITUTE_HEAD."""
    if current_user.role not in [models.UserRole.WARDEN.value, models.UserRole.INSTITUTE_HEAD.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Warden or Institute Head privileges required",
        )
    return current_user


def get_current_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """Ensure the authenticated user is an INSTITUTE_HEAD (admin)."""
    if current_user.role != models.UserRole.INSTITUTE_HEAD.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: INSTITUTE_HEAD privileges required",
        )
    return current_user


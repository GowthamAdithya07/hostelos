from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, models, crud
from ..auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserRegister, db: Session = Depends(get_db)):
    """Register a new account (role defaults to USER)."""
    existing_user = crud.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Standard registration always defaults to USER unless INSTITUTE_HEAD was explicitly allowed
    user = crud.create_user(db, user_in)
    return user


@router.post("/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email and password to receive JWT tokens."""
    user = crud.get_user_by_email(db, login_data.email)
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email, "role": user.role})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/refresh")
def refresh_token(token_data: schemas.TokenRefresh, db: Session = Depends(get_db)):
    """Generate a new access token using a valid refresh token."""
    payload = decode_token(token_data.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Expected refresh token.",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )

    user = crud.get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token no longer exists",
        )

    new_access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: Any = Depends(get_current_user)):
    """Fetch current authenticated user profile."""
    return current_user


@router.get("/accounts", response_model=List[schemas.UserSummary])
def get_interconnected_accounts(db: Session = Depends(get_db)):
    """List all registered campus accounts for interconnected switcher."""
    users = crud.get_all_users(db, skip=0, limit=50)
    return users


@router.post("/switch", response_model=schemas.Token)
def quick_switch_account(switch_in: schemas.QuickSwitchRequest, db: Session = Depends(get_db)):
    """
    Seamlessly switch identity to another campus account.
    Enables instant cross-account collaboration and multi-user testing.
    """
    user = crud.get_user_by_email(db, switch_in.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campus account with email '{switch_in.email}' not found.",
        )

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email, "role": user.role})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }

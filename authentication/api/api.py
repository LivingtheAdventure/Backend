from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from database.database import get_db

from authentication.model.model import User
from authentication.schema.schema import (
    RequestEmailOTPRequest,
    UpdateUserRequest,
    VerifyEmailOTPRequest,
    SignupCompleteRequest,
    AdminUsersResponse,
)

from authentication.service.service import (
    firebase_auth_dep,
    _send_otp_email,
    get_admin_users,
)

from authentication.service.otp_store import otp_store

from admin.service.service import get_current_admin

from logs.service.service import create_user_action_log

router = APIRouter(prefix="/auth", tags=["auth"])


# ─── Constants ────────────────────────────────────────────────────────────────

OTP_TTL_MINUTES = 10
OTP_MAX_ATTEMPTS = 20
OTP_RESEND_COOLDOWN_SEC = 60


# ─── Signup ───────────────────────────────────────────────────────────────────


@router.post("/signup/complete")
def signup_complete(
    payload: SignupCompleteRequest,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    phone = decoded.get("phone_number")

    existing = db.query(User).filter(User.phone == phone).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="User already exists",
        )

    try:
        user = User(
            phone=phone,
            first_name=payload.first_name,
            last_name=payload.last_name,
            is_verified=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        create_user_action_log(
            db=db,
            user_id=user.user_id,
            action="USER_SIGNUP",
            entity="USER",
            entity_id=str(user.user_id),
            description="User account was created successfully",
        )

        return user

    except Exception:
        db.rollback()

        # No user_id may exist if creation itself failed,
        # so we don't create a user-action log here.

        raise


# ─── Firebase Verify ──────────────────────────────────────────────────────────


@router.post("/firebase/verify")
def firebase_verify(
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    phone = decoded.get("phone_number")

    user = db.query(User).filter(User.phone == phone).first()

    if user:

        create_user_action_log(
            db=db,
            user_id=user.user_id,
            action="USER_LOGIN",
            entity="USER",
            entity_id=str(user.user_id),
            description="User logged in successfully",
        )

        return {
            "status": "LOGIN",
            "user": user,
        }

    return {
        "status": "SIGNUP_REQUIRED",
        "phone": phone,
    }


# ─── Get Current User ─────────────────────────────────────────────────────────


@router.get("/me")
def get_me(
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    phone = decoded.get("phone_number")

    user = db.query(User).filter(User.phone == phone).first()

    if not user:
        return None

    return user


# ─── Update Current User ──────────────────────────────────────────────────────


@router.put("/me")
def update_me(
    payload: UpdateUserRequest,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    phone = decoded.get("phone_number")

    user = db.query(User).filter(User.phone == phone).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    try:
        if payload.first_name is not None:
            user.first_name = payload.first_name

        if payload.last_name is not None:
            user.last_name = payload.last_name

        if payload.email is not None:
            user.email = payload.email

        db.commit()
        db.refresh(user)

        create_user_action_log(
            db=db,
            user_id=user.user_id,
            action="USER_PROFILE_UPDATED",
            entity="USER",
            entity_id=str(user.user_id),
            description="User profile was updated successfully",
        )

        return user

    except Exception:
        db.rollback()

        create_user_action_log(
            db=db,
            user_id=user.user_id,
            action="USER_PROFILE_UPDATED",
            entity="USER",
            entity_id=str(user.user_id),
            description="Failed to update user profile",
        )

        raise


# ─── Admin: Get Users ─────────────────────────────────────────────────────────


@router.get(
    "/users",
    response_model=AdminUsersResponse,
)
def read_users(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
    active: bool | None = None,
    verified: bool | None = None,
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin),
):
    return get_admin_users(
        db=db,
        page=page,
        limit=limit,
        search=search,
        active=active,
        verified=verified,
    )

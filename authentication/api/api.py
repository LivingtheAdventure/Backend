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
    SignupCompleteRequest
)
from authentication.service.service import firebase_auth_dep, _send_otp_email
from authentication.service.otp_store import otp_store   # ← new module (see otp_store.py)

router = APIRouter(prefix="/auth", tags=["auth"])

# ─── Constants ────────────────────────────────────────────────────────────────
OTP_TTL_MINUTES   = 10
OTP_MAX_ATTEMPTS  = 20        # wrong guesses before the record is wiped
OTP_RESEND_COOLDOWN_SEC = 60   # minimum seconds between resend requests


# ─── Existing endpoints (unchanged) ──────────────────────────────────────────

@router.post("/signup/complete")
def signup_complete(
    payload: SignupCompleteRequest,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db)
):
    phone = decoded.get("phone_number")

    existing = db.query(User).filter(User.phone == phone).first()
    if existing:
        raise HTTPException(409, "User already exists")

    user = User(
        phone=phone,
        first_name=payload.first_name,
        last_name=payload.last_name,
        is_verified=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.post("/firebase/verify")
def firebase_verify(decoded=Depends(firebase_auth_dep), db: Session = Depends(get_db)):
    phone = decoded.get("phone_number")

    user = db.query(User).filter(User.phone == phone).first()

    if user:
        return {"status": "LOGIN", "user": user}

    return {"status": "SIGNUP_REQUIRED", "phone": phone}



@router.get("/me")
def get_me(decoded=Depends(firebase_auth_dep), db: Session = Depends(get_db)):
    phone = decoded.get("phone_number")
    user  = db.query(User).filter(User.phone == phone).first()
    if not user:
        return None
    return user


@router.put("/me")
def update_me(
    payload: UpdateUserRequest,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    phone = decoded.get("phone_number")
    user  = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.email is not None:
        user.email = payload.email

    db.commit()
    db.refresh(user)
    return user

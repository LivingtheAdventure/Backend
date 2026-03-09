from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from firebase_admin import auth
from datetime import datetime, timedelta
from database.database import get_db
from authentication.model.model import User
from authentication.schema.schema import RequestEmailOTPRequest,UpdateEmailRequest,UpdateUserRequest,VerifyEmailOTPRequest,FirebaseVerifyResponse
from authentication.service.service import firebase_auth_dep,_send_otp_email
import random

router = APIRouter(prefix="/auth", tags=["auth"])

_otp_store: dict = {}

@router.post("/firebase/verify")
def firebase_verify(decoded=Depends(firebase_auth_dep), db: Session = Depends(get_db)):

    phone = decoded.get("phone_number")

    user = db.query(User).filter(User.phone == phone).first()

    if user:
        return {
            "status": "LOGIN",
            "user_id": str(user.user_id)
        }

    return {
        "status": "SIGNUP_REQUIRED",
        "phone": phone
    }

@router.post("/signup")
def signup(
    first_name: str,
    last_name: str,
    email: str | None = None,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):

    phone = decoded.get("phone_number")

    existing = db.query(User).filter(User.phone == phone).first()

    if existing:
        return existing

    user = User(
        phone=phone,
        first_name=first_name,
        last_name=last_name,
        email=email
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.get("/me")
def get_me(decoded=Depends(firebase_auth_dep), db: Session = Depends(get_db)):
    phone = decoded.get("phone_number")
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        return None
    return user


@router.put("/me")
def update_me(
    payload: UpdateUserRequest,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    """Update first_name and/or last_name. Email is handled separately via OTP."""
    phone = decoded.get("phone_number")
    user = db.query(User).filter(User.phone == phone).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name

    db.commit()
    db.refresh(user)
    return user


@router.post("/me/request-email-otp")
def request_email_otp(
    payload: RequestEmailOTPRequest,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    """Send a 6-digit OTP to the requested email address."""
    phone = decoded.get("phone_number")

    # Check email not already taken by another user
    existing = db.query(User).filter(
        User.email == payload.email,
        User.phone != phone
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email is already in use by another account."
        )

    otp = str(random.randint(100000, 999999))
    _otp_store[phone] = {
        "otp": otp,
        "email": payload.email,
        "expires": datetime.utcnow() + timedelta(minutes=10),
    }

    try:
        _send_otp_email(payload.email, otp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    return {"message": "OTP sent to email"}


@router.post("/me/verify-email-otp")
def verify_email_otp(
    payload: VerifyEmailOTPRequest,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    """Verify OTP and update the user's email."""
    phone = decoded.get("phone_number")
    record = _otp_store.get(phone)

    if not record:
        raise HTTPException(status_code=400, detail="No OTP requested. Please request a new one.")

    if datetime.utcnow() > record["expires"]:
        del _otp_store[phone]
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")

    if record["otp"] != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    if record["email"] != payload.email:
        raise HTTPException(status_code=400, detail="Email mismatch.")

    # All good — update the email
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email = payload.email
    user.is_verified = True
    db.commit()
    db.refresh(user)

    del _otp_store[phone]  # consume OTP
    return {"message": "Email verified and updated", "email": user.email}
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
)
from authentication.service.service import firebase_auth_dep, _send_otp_email
from authentication.service.otp_store import otp_store   # ← new module (see otp_store.py)

router = APIRouter(prefix="/auth", tags=["auth"])

# ─── Constants ────────────────────────────────────────────────────────────────
OTP_TTL_MINUTES   = 10
OTP_MAX_ATTEMPTS  = 5          # wrong guesses before the record is wiped
OTP_RESEND_COOLDOWN_SEC = 60   # minimum seconds between resend requests


# ─── Existing endpoints (unchanged) ──────────────────────────────────────────

@router.post("/firebase/verify")
def firebase_verify(decoded=Depends(firebase_auth_dep), db: Session = Depends(get_db)):
    phone = decoded.get("phone_number")
    user  = db.query(User).filter(User.phone == phone).first()
    if user:
        return {"status": "LOGIN",           "user_id": str(user.user_id)}
    return  {"status": "SIGNUP_REQUIRED",    "phone":   phone}


@router.post("/signup")
def signup(
    first_name: str,
    last_name:  str,
    email:      str | None = None,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    phone    = decoded.get("phone_number")
    existing = db.query(User).filter(User.phone == phone).first()
    if existing:
        return existing

    user = User(phone=phone, first_name=first_name, last_name=last_name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


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

    db.commit()
    db.refresh(user)
    return user


# ─── OTP endpoints (production-hardened) ─────────────────────────────────────

@router.post("/me/request-email-otp", status_code=200)
def request_email_otp(
    payload: RequestEmailOTPRequest,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    """
    Send a 6-digit OTP to the requested e-mail address.

    Guards:
    • Rejects if the e-mail is already this user's verified e-mail.
    • Rejects if the e-mail belongs to another account.
    • Enforces a 60-second cool-down between resend requests.
    """
    phone = decoded.get("phone_number")
    user  = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_email = payload.email.strip().lower()

    # 1. Already this user's verified e-mail?
    if user.email and user.email.lower() == new_email and user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email is already verified on your account.",
        )

    # 2. Taken by another account?
    conflict = db.query(User).filter(
        User.email == new_email,
        User.phone != phone,
        User.is_verified == True,           # noqa: E712
    ).first()
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email is already in use by another account.",
        )

    # 3. Cool-down check (prevent spam / resend flooding)
    existing = otp_store.get(phone)
    if existing:
        elapsed = (datetime.utcnow() - existing["requested_at"]).total_seconds()
        if elapsed < OTP_RESEND_COOLDOWN_SEC:
            wait = int(OTP_RESEND_COOLDOWN_SEC - elapsed)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {wait} seconds before requesting another code.",
            )

    # 4. Generate cryptographically-secure OTP
    otp = str(secrets.randbelow(900000) + 100000)   # always 6 digits, crypto-safe

    otp_store.set(phone, {
        "otp":          otp,
        "email":        new_email,
        "expires":      datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES),
        "requested_at": datetime.utcnow(),
        "attempts":     0,
    })

    try:
        _send_otp_email(new_email, otp)
    except Exception as e:
        otp_store.delete(phone)          # clean up so user can retry immediately
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    return {"message": "Verification code sent.", "cooldown_seconds": OTP_RESEND_COOLDOWN_SEC}


@router.post("/me/verify-email-otp", status_code=200)
def verify_email_otp(
    payload: VerifyEmailOTPRequest,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    """
    Verify OTP and update the user's e-mail.

    Guards:
    • Rejects expired OTPs.
    • Rejects after OTP_MAX_ATTEMPTS wrong guesses (brute-force protection).
    • Uses constant-time comparison to prevent timing attacks.
    """
    phone  = decoded.get("phone_number")
    record = otp_store.get(phone)

    # Generic "invalid" message — don't reveal whether record exists
    _invalid = HTTPException(status_code=400, detail="Invalid or expired verification code.")

    if not record:
        raise _invalid

    # Expired?
    if datetime.utcnow() > record["expires"]:
        otp_store.delete(phone)
        raise HTTPException(status_code=400, detail="Verification code has expired. Please request a new one.")

    # Too many wrong attempts?
    if record["attempts"] >= OTP_MAX_ATTEMPTS:
        otp_store.delete(phone)
        raise HTTPException(
            status_code=400,
            detail="Too many incorrect attempts. Please request a new code.",
        )

    # Constant-time OTP comparison (prevent timing attacks)
    submitted_email = payload.email.strip().lower()
    otp_matches     = secrets.compare_digest(record["otp"], payload.otp)
    email_matches   = secrets.compare_digest(record["email"], submitted_email)

    if not otp_matches or not email_matches:
        record["attempts"] += 1
        otp_store.set(phone, record)      # persist incremented attempt count
        remaining = OTP_MAX_ATTEMPTS - record["attempts"]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid code. {remaining} attempt(s) remaining.",
        )

    # ── All checks passed — update the user ──────────────────────────────────
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email       = submitted_email
    user.is_verified = True
    db.commit()
    db.refresh(user)

    otp_store.delete(phone)   # consume OTP immediately

    return {"message": "Email verified and updated.", "email": user.email}
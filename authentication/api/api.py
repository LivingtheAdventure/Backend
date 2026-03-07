from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from firebase_admin import auth

from database.database import get_db
from authentication.model.model import User
from authentication.service.service import firebase_auth_dep

router = APIRouter(prefix="/auth", tags=["auth"])


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
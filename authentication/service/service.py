import os
import json
import base64
import firebase_admin

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from firebase_admin import auth, credentials

from database.database import get_db
from authentication.model.model import User

security = HTTPBearer()

firebase_base64 = os.getenv("FIREBASE_CREDENTIALS_BASE64")

if not firebase_admin._apps:

    if not firebase_base64:
        raise RuntimeError("FIREBASE_CREDENTIALS_BASE64 not set")

    cred_json = base64.b64decode(firebase_base64).decode("utf-8")
    cred_dict = json.loads(cred_json)

    cred = credentials.Certificate(cred_dict)

    firebase_admin.initialize_app(cred)


def firebase_auth_dep(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):

    token = credentials.credentials

    try:
        decoded = auth.verify_id_token(token)
        return decoded

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid Firebase token"
        )


def get_current_user(
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):

    phone = decoded.get("phone_number")

    if not phone:
        raise HTTPException(
            status_code=400,
            detail="Phone number not found in token"
        )

    user = db.query(User).filter(User.phone == phone).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user
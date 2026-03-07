from fastapi import Header, HTTPException
import os
from sqlalchemy.orm import Session
from database.database import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from authentication.model.model import User
from fastapi import Depends
import firebase_admin
from firebase_admin import auth, credentials

security = HTTPBearer()

service_account_path = "../../living-the-adventure-firebase-adminsdk-fbsvc-1eb54110fb.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)


def firebase_auth_dep(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

def get_current_user(
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):

    phone = decoded.get("phone_number")

    if not phone:
        raise HTTPException(status_code=400, detail="Phone number not found in token")

    user = db.query(User).filter(User.phone == phone).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
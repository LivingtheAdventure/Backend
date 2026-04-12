from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Header, Depends
from sqlalchemy.orm import Session
import os
from admin.model.model import Admin
from database.database import get_db
ADMIN_ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ADMIN_ACCESS_TOKEN_EXPIRE_HOURS"))
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")
ADMIN_ALGORITHM = os.getenv("ADMIN_ALGORITHM")


# 🔐 Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ADMIN_ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, ADMIN_SECRET_KEY, algorithm=ADMIN_ALGORITHM)


# 🔐 Authenticate Admin
def authenticate_admin(db: Session, email: str, password: str):
    admin = db.query(Admin).filter(Admin.email == email).first()

    if not admin or not verify_password(password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return admin


# 🔒 Dependency for protected routes
def get_current_admin(token: str = Header(None), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        payload = jwt.decode(token, ADMIN_SECRET_KEY, algorithms=[ADMIN_ALGORITHM])
        admin_id = payload.get("admin_id")

        if not admin_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()

        if not admin:
            raise HTTPException(status_code=401, detail="Admin not found")

        return admin_id

    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
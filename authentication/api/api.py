from datetime import timedelta
from typing import Annotated
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from database.database import get_db
from authentication.schema.schema import User
from authentication.model.model import UserRead, Token , CreateUserWithEmail , CreateUserWithPhone

from auth.security import verify_password, get_password_hash, create_access_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

# ---------- Helpers ----------
def get_user_by_id(db: Session, tenant_id: UUID) -> User | None:
    return db.query(User).filter(User.tenant_id == tenant_id).first()

# Dependency to fetch current user from bearer token
async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub: str | None = payload.get("sub")
        if sub is None:
            raise credentials_exception
        tenant_id = UUID(sub)
    except (JWTError, ValueError):
        raise credentials_exception

    user = get_user_by_id(db, tenant_id)
    if user is None:
        raise credentials_exception
    return user

# Register with Email
@router.post("/register/email", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_with_email(payload: CreateUserWithEmail, db: Annotated[Session, Depends(get_db)]):
    # check if email already exists
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        tenant_id=uuid4(),  # generate new uuid automatically
        email=payload.email,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Register with Phone Number
@router.post("/register/phone", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_with_phone(payload: CreateUserWithPhone, db: Annotated[Session, Depends(get_db)]):
    # check if phone number already exists
    existing = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    user = User(
        tenant_id=uuid4(),
        phone_number=payload.phone_number,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    username = form_data.username
    password = form_data.password

    # Try lookup by email
    user = db.query(User).filter(User.email == username).first()

    # If not found, try lookup by phone
    if not user:
        user = db.query(User).filter(User.phone_number == username).first()

    # If not found, maybe it's a tenant_id (UUID)
    if not user:
        try:
            tenant_id = UUID(username)
            user = get_user_by_id(db, tenant_id)
        except ValueError:
            pass  # not a valid UUID, ignore

    # If still not found → invalid credentials
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT
    access_token = create_access_token(
        data={"sub": str(user.tenant_id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

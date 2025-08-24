from datetime import timedelta,datetime
from uuid import uuid4
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database.database import get_db
from authentication.schema.schema import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
outh2_barrier = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateUserRequest(BaseModel):
    tenant_id:uuid4
    password:str

class Tocken(BaseModel):
    access_token:str
    token_type: str

db_dependancy = Annotated[Session,Depends(get_db)]
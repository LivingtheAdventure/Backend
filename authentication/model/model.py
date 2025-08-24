from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class CreateUserWithEmail(BaseModel):
    email: EmailStr
    password: str

class CreateUserWithPhone(BaseModel):
    phone_number: str
    password: str

class UserRead(BaseModel):
    tenant_id: UUID
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    user_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True  # pydantic v2: allow ORM -> schema

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

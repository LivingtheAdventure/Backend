from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional,List



class SignupCompleteRequest(BaseModel):
    first_name: str
    last_name: str

class UserResponse(BaseModel):
    user_id: UUID
    phone: str
    is_verified: bool
    is_active: bool
class FirebaseVerifyResponse(BaseModel):
    status: str  # LOGIN | SIGNUP_REQUIRED
    user: UserResponse | None = None
    phone: str | None = None
    class Config:
        from_attributes = True

class UpdateUserRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email : Optional[EmailStr] = None

class RequestEmailOTPRequest(BaseModel):
    email: EmailStr

class VerifyEmailOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class UpdateEmailRequest(BaseModel):
    email: EmailStr
    otp: str

class AdminUserOut(BaseModel):
    user_id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    phone: str
    email: Optional[EmailStr]
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class AdminUsersResponse(BaseModel):
    total: int
    page: int
    limit: int
    users: List[AdminUserOut]
from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional


class SignupCompleteRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None

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

class RequestEmailOTPRequest(BaseModel):
    email: EmailStr

class VerifyEmailOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class UpdateEmailRequest(BaseModel):
    email: EmailStr
    otp: str

from pydantic import BaseModel, EmailStr

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminResponse(BaseModel):
    admin_id: str
    email: str

    class Config:
        from_attributes = True


class AdminLoginResponse(BaseModel):
    access_token: str
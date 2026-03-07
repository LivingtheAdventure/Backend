import uuid
from database.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__= "users"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id=Column(  UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False)
    first_name=Column(String,nullable=True)
    last_name=Column(String,nullable=True)
    phone= Column(String, unique=True,nullable=False)
    email= Column(String, unique=True,nullable=True)
    is_active= Column(Boolean, default=True)
    is_verified= Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class OTPLog(Base):
    __tablename__ = "otp_logs"

    id = Column(Integer, primary_key=True)
    phone = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Config:
    from_attributes = True

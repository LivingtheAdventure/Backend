from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserActionLogBase(BaseModel):
    user_id: UUID

    action: str
    entity: Optional[str] = None
    entity_id: Optional[str] = None
    description: Optional[str] = None
    extra_data: Optional[dict] = None


class UserActionLogCreate(UserActionLogBase):
    pass


class UserActionLogResponse(UserActionLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

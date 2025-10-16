from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime

class EventScheduleBase(BaseModel):
    event_id: UUID
    schedule_data: Any
    status: Optional[str] = None

class EventScheduleCreate(EventScheduleBase):
    schedule_id: Optional[UUID] = None

class EventScheduleUpdate(EventScheduleBase):
    pass

class EventScheduleOut(EventScheduleBase):
    id: int
    schedule_id: Optional[UUID] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

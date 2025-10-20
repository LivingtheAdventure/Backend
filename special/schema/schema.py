from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

# ---- CREATE ----
class CreateBestOFTheYear(BaseModel):
    event: UUID
    status: Optional[str] = None


class CreateUpcommingEvent(BaseModel):
    event: UUID
    status: Optional[str] = None


# ---- OUTPUT ----
class BestOFTheYearOut(BaseModel):
    id: int
    bestoftheyear_id: UUID
    event_id: UUID
    status: Optional[str]

    class Config:
        orm_mode = True


class UpcommingEventsOut(BaseModel):
    id: int
    upcomming_event_id: UUID
    event_id: UUID
    status: Optional[str]

    class Config:
        orm_mode = True

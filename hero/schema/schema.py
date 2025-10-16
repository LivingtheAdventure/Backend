from typing import List, Optional, Union
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, AnyUrl

class HeroBase(BaseModel):
    title: Optional[str] = None
    rank: Optional[int] = None
    video_url: Optional[AnyUrl] = None
    thumbnail_image_url: Optional[AnyUrl] = None
    description: Optional[str] = None
    details: Optional[List[str]] = None
    genres: Optional[List[str]] = None
    status: Optional[str] = None
    # FIX: Allow 'active' to be either a boolean or a string
    active: Optional[Union[str, bool]] = None

class HeroCreate(HeroBase):
    hero_id: Optional[UUID] = None
    event_id: UUID

class HeroUpdate(BaseModel):
    title: Optional[str] = None
    rank: Optional[int] = None
    video_url: Optional[AnyUrl] = None
    thumbnail_image_url: Optional[AnyUrl] = None
    description: Optional[str] = None
    details: Optional[List[str]] = None
    genres: Optional[List[str]] = None
    status: Optional[str] = None
    # FIX: Allow 'active' to be either a boolean or a string
    active: Optional[Union[str, bool]] = None

class HeroOut(HeroBase):
    id: int
    hero_id: Optional[UUID] = None
    event_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

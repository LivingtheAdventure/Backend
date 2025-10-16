from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, AnyUrl

class EventBase(BaseModel):
    title: str
    event_type: str
    adventure_activity_category: Optional[str] = None
    adventure_difficulty_level: Optional[str] = None
    trek_difficulty_level: Optional[str] = None
    peak_difficulty_level: Optional[str] = None
    peak_group_type: Optional[str] = None

    age_requirement: Optional[int] = None
    fitness_requirement: Optional[str] = None
    location: Optional[str] = None

    duration_days: Optional[int] = None
    duration_nights: Optional[int] = None

    short_description: Optional[str] = None
    itinerary: Optional[str] = None
    highlights: Optional[List[str]] = None

    cover_image_url: Optional[AnyUrl] = None
    poster_horizontal_1_url: Optional[AnyUrl] = None
    poster_horizontal_2_url: Optional[AnyUrl] = None
    poster_vertical_3_url: Optional[AnyUrl] = None
    gallery_image_urls: Optional[List[AnyUrl]] = None
    promo_video_url: Optional[AnyUrl] = None

    max_participants_allowed: Optional[int] = None
    included_services: Optional[List[str]] = None
    excluded_services: Optional[List[str]] = None

    safety_guidelines_text: Optional[str] = None
    cancellation_policy_text: Optional[str] = None

    seo_tags: Optional[List[str]] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None

    status: Optional[str] = None


class EventCreate(EventBase):
    event_id: Optional[UUID] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    event_type: Optional[str] = None
    adventure_activity_category: Optional[str] = None
    adventure_difficulty_level: Optional[str] = None
    trek_difficulty_level: Optional[str] = None
    peak_difficulty_level: Optional[str] = None
    peak_group_type: Optional[str] = None
    age_requirement: Optional[int] = None
    fitness_requirement: Optional[str] = None
    location: Optional[str] = None
    duration_days: Optional[int] = None
    duration_nights: Optional[int] = None
    short_description: Optional[str] = None
    itinerary: Optional[str] = None
    highlights: Optional[List[str]] = None
    cover_image_url: Optional[AnyUrl] = None
    poster_horizontal_1_url: Optional[AnyUrl] = None
    poster_horizontal_2_url: Optional[AnyUrl] = None
    poster_vertical_3_url: Optional[AnyUrl] = None
    gallery_image_urls: Optional[List[AnyUrl]] = None
    promo_video_url: Optional[AnyUrl] = None
    max_participants_allowed: Optional[int] = None
    included_services: Optional[List[str]] = None
    excluded_services: Optional[List[str]] = None
    safety_guidelines_text: Optional[str] = None
    cancellation_policy_text: Optional[str] = None
    seo_tags: Optional[List[str]] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    status: Optional[str] = None


class EventOut(EventBase):
    id: int
    event_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
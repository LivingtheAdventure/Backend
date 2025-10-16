from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ARRAY, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from database.database import Base
import uuid

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(PG_UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=True)

    title = Column(String, nullable=False)
    event_type = Column(String, nullable=False)

    adventure_activity_category = Column(String, nullable=True)
    adventure_difficulty_level = Column(String, nullable=True)
    trek_difficulty_level = Column(String, nullable=True)
    peak_difficulty_level = Column(String, nullable=True)
    peak_group_type = Column(String, nullable=True)

    age_requirement = Column(Integer, nullable=True)
    fitness_requirement = Column(Text, nullable=True)
    location = Column(String, nullable=True)

    duration_days = Column(Integer, nullable=True)
    duration_nights = Column(Integer, nullable=True)

    short_description = Column(Text, nullable=True)
    itinerary = Column(Text, nullable=True)
    highlights = Column(ARRAY(String), nullable=True)

    cover_image_url = Column(String, nullable=True)
    poster_horizontal_1_url = Column(String, nullable=True)
    poster_horizontal_2_url = Column(String, nullable=True)
    poster_vertical_3_url = Column(String, nullable=True)
    gallery_image_urls = Column(ARRAY(String), nullable=True)
    promo_video_url = Column(String, nullable=True)

    max_participants_allowed = Column(Integer, nullable=True)
    included_services = Column(ARRAY(String), nullable=True)
    excluded_services = Column(ARRAY(String), nullable=True)

    safety_guidelines_text = Column(Text, nullable=True)
    cancellation_policy_text = Column(Text, nullable=True)

    seo_tags = Column(ARRAY(String), nullable=True)
    seo_title = Column(String, nullable=True)
    seo_description = Column(Text, nullable=True)

    status = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())
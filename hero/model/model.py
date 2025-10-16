# app/models/hero.py
import uuid
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from database.database import Base # Make sure this import is correct for your project

class Hero(Base):
    __tablename__ = "heroes"

    id = Column(Integer, primary_key=True, index=True)
    hero_id = Column(UUID(as_uuid=True), unique=True, nullable=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    rank = Column(Integer, nullable=True)
    title = Column(String, nullable=True) # CHANGED: Varchar doesn't need a length and is nullable
    video_url = Column(String, nullable=True) # CHANGED: Varchar is String in SQLAlchemy
    thumbnail_image_url = Column(String, nullable=True) # CHANGED: Varchar is String in SQLAlchemy
    description = Column(String, nullable=True) # CHANGED: Varchar is String in SQLAlchemy

    # CRITICAL FIX: Changed from JSONB to ARRAY(String) to match the database
    details = Column(ARRAY(String), nullable=True)

    genres = Column(ARRAY(String), nullable=True)
    status = Column(String, nullable=True)

    # CHANGED: 'active' column in the DB is 'character varying', not boolean
    active = Column(String, nullable=True)

    # CHANGED: DB is 'timestamp without time zone' and nullable
    created_at = Column(DateTime, nullable=True, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.database import Base

class EventSchedule(Base):
    __tablename__ = "event_schedules"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(UUID(as_uuid=True))
    event_id = Column(UUID(as_uuid=True), nullable=False)
    schedule_data = Column(JSONB, nullable=False)
    status = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

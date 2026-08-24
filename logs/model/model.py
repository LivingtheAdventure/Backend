from database.database import Base

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB


class SystemLogs(Base):
    __tablename__ = "systemlogs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    action = Column(String, nullable=False, index=True)

    entity = Column(String, nullable=True)

    entity_id = Column(String, nullable=True)

    description = Column(String, nullable=True)

    extra_data = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

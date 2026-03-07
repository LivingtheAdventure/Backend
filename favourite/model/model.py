from database.database import Base
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID


class Favourite(Base):
    __tablename__ = "favourites"

    id = Column(Integer, primary_key=True)

    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)

    event_id = Column(UUID(as_uuid=True), index=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
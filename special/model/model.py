from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from database.database import Base

class BestOFTheYear(Base):
    __tablename__ = "best_of_the_year"

    id = Column(Integer, primary_key=True, index=True)
    bestoftheyear_id = Column(UUID(as_uuid=True))
    event_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String, nullable=True)


class UpcommingEvents(Base):
    __tablename__ = "upcomming_event"

    id = Column(Integer, primary_key=True, index=True)
    upcomming_event_id = Column(UUID(as_uuid=True))
    event_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String, nullable=True)

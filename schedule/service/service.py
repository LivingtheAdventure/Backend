from sqlalchemy.orm import Session
from uuid import uuid4
from schedule.model.model import EventSchedule
from schedule.schema.schema import EventScheduleCreate, EventScheduleUpdate

def get_event_schedules(db: Session, skip: int = 0, limit: int = 50):
    return db.query(EventSchedule).offset(skip).limit(limit).all()

def get_event_schedule_by_id(db: Session, schedule_id: int):
    return db.query(EventSchedule).filter(EventSchedule.id == schedule_id).first()

def get_event_schedule_by_uuid(db: Session, schedule_uuid):
    return db.query(EventSchedule).filter(EventSchedule.schedule_id == schedule_uuid).first()

def create_event_schedule(db: Session, payload: EventScheduleCreate):
    schedule_uuid = payload.schedule_id or uuid4()
    db_schedule = EventSchedule(
        schedule_id=schedule_uuid,
        event_id=payload.event_id,
        schedule_data=payload.schedule_data,
        status=payload.status,
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def update_event_schedule(db: Session, db_schedule: EventSchedule, payload: EventScheduleUpdate):
    db_schedule.schedule_data = payload.schedule_data
    db_schedule.status = payload.status
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def delete_event_schedule(db: Session, db_schedule: EventSchedule):
    db.delete(db_schedule)
    db.commit()

def get_event_schedules_by_event_id(db: Session, event_id):
    return db.query(EventSchedule).filter(EventSchedule.event_id == event_id).all()

from sqlalchemy.orm import Session
from uuid import uuid4
from special.model.model import BestOFTheYear, UpcommingEvents

# ----------- Best Of The Year -----------

def get_best_of_the_year(db: Session, skip: int = 0, limit: int = 50):
    return db.query(BestOFTheYear).offset(skip).limit(limit).all()

def get_best_of_the_year_by_uuid(db: Session, bestofyear_uuid):
    return db.query(BestOFTheYear).filter(BestOFTheYear.bestoftheyear_id == bestofyear_uuid).first()


def get_best_of_the_year_by_id(db: Session, id: int):
    return db.query(BestOFTheYear).filter(BestOFTheYear.id == id).first()


def create_best_of_the_year(db: Session, event_id, status=None):
    new_item = BestOFTheYear(
        bestoftheyear_id=uuid4(),
        event_id=event_id,
        status=status
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


def delete_best_of_the_year(db: Session, id: int):
    item = db.query(BestOFTheYear).filter(BestOFTheYear.id == id).first()
    if item:
        db.delete(item)
        db.commit()
    return item


# ----------- Upcoming Events -----------

def get_upcomming_events(db: Session, skip: int = 0, limit: int = 50):
    return db.query(UpcommingEvents).offset(skip).limit(limit).all()


def get_upcoming_event_by_uuid(db: Session, event_uuid):
    return db.query(UpcommingEvents).filter(UpcommingEvents.upcomming_event_id == event_uuid).first()


def get_upcomming_event_by_id(db: Session, id: int):
    return db.query(UpcommingEvents).filter(UpcommingEvents.id == id).first()


def create_upcomming_event(db: Session, event_id, status=None):
    new_event = UpcommingEvents(
        upcomming_event_id=uuid4(),
        event_id=event_id,
        status=status
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


def delete_upcomming_event(db: Session, id: int):
    event = db.query(UpcommingEvents).filter(UpcommingEvents.id == id).first()
    if event:
        db.delete(event)
        db.commit()
    return event

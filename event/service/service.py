from sqlalchemy.orm import Session
from uuid import uuid4
from event.model.model import Event
from event.schema.schema import EventCreate, EventUpdate

def get_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Event).offset(skip).limit(limit).all()

def get_event_by_id(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

def get_event_by_uuid(db: Session, event_uuid):
    return db.query(Event).filter(Event.event_id == event_uuid).first()

def create_event(db: Session, event_in: EventCreate):
    event_data = event_in.dict(exclude_unset=True)

    # Convert AnyUrl -> str
    for field in [
        "cover_image_url",
        "poster_horizontal_1_url",
        "poster_horizontal_2_url",
        "poster_vertical_3_url",
        "promo_video_url",
    ]:
        if field in event_data and event_data[field] is not None:
            event_data[field] = str(event_data[field])

    if event_data.get("gallery_image_urls"):
        event_data["gallery_image_urls"] = [str(url) for url in event_data["gallery_image_urls"]]

    # Ensure event_id exists
    if not event_data.get("event_id"):
        event_data["event_id"] = uuid4()

    db_obj = Event(**event_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_event(db: Session, db_obj: Event, event_in: EventUpdate):
    update_data = event_in.dict(exclude_unset=True)

    for field, value in update_data.items():
        if hasattr(db_obj, field):
            if "url" in field and value is not None:
                value = str(value)
            setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_event(db: Session, db_obj: Event):
    db.delete(db_obj)
    db.commit()
    return
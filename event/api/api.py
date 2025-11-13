from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database.database import get_db
from event.service.service import (
    get_events,
    get_event_by_id,
    get_event_by_uuid,
    create_event,
    get_events_by_type,
    update_event,
    delete_event
)
from event.schema.schema import EventOut, EventCreate, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=List[EventOut])
def list_events(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return get_events(db, skip=skip, limit=limit)

@router.get("/{event_id}", response_model=EventOut)
def read_event(event_id: int, db: Session = Depends(get_db)):
    db_event = get_event_by_id(db, event_id)
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return db_event

@router.get("/by-uuid/{event_uuid}", response_model=EventOut)
def read_event_by_uuid(event_uuid: UUID, db: Session = Depends(get_db)):
    db_event = get_event_by_uuid(db, event_uuid)
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return db_event

@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_new_event(payload: EventCreate, db: Session = Depends(get_db)):
    created = create_event(db, payload)
    return created

@router.put("/{event_id}", response_model=EventOut)
def update_existing_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)):
    db_event = get_event_by_id(db, event_id)
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    updated = update_event(db, db_event, payload)
    return updated

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_event(event_id: int, db: Session = Depends(get_db)):
    db_event = get_event_by_id(db, event_id)
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    delete_event(db, db_event)
    return  

@router.get("/by-type/{event_type}", response_model=List[EventOut])
def read_events_by_type(event_type: str, db: Session = Depends(get_db)):
    events = get_events_by_type(db, event_type)
    if not events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No events found for this type")
    return events

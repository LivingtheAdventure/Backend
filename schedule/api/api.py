from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database.database import get_db
from schedule.service.service import (
    get_event_schedules,
    get_event_schedule_by_id,
    get_event_schedule_by_uuid,
    create_event_schedule,
    update_event_schedule,
    delete_event_schedule,
    get_event_schedules_by_event_id
)
from schedule.schema.schema import EventScheduleOut, EventScheduleCreate, EventScheduleUpdate

router = APIRouter(prefix="/event-schedules", tags=["Event Schedules"])

@router.get("/", response_model=List[EventScheduleOut])
def list_event_schedules(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return get_event_schedules(db, skip, limit)

@router.get("/{schedule_id}", response_model=EventScheduleOut)
def read_event_schedule(schedule_id: int, db: Session = Depends(get_db)):
    db_schedule = get_event_schedule_by_id(db, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    return db_schedule

@router.get("/by-uuid/{schedule_uuid}", response_model=EventScheduleOut)
def read_event_schedule_by_uuid(schedule_uuid: UUID, db: Session = Depends(get_db)):
    db_schedule = get_event_schedule_by_uuid(db, schedule_uuid)
    if not db_schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    return db_schedule

@router.post("/", response_model=EventScheduleOut, status_code=status.HTTP_201_CREATED)
def create_new_event_schedule(payload: EventScheduleCreate, db: Session = Depends(get_db)):
    return create_event_schedule(db, payload)

@router.put("/{schedule_id}", response_model=EventScheduleOut)
def update_existing_event_schedule(schedule_id: int, payload: EventScheduleUpdate, db: Session = Depends(get_db)):
    db_schedule = get_event_schedule_by_id(db, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    return update_event_schedule(db, db_schedule, payload)

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_event_schedule(schedule_id: int, db: Session = Depends(get_db)):
    db_schedule = get_event_schedule_by_id(db, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    delete_event_schedule(db, db_schedule)
    return

@router.get("/by-event/{event_id}", response_model=List[EventScheduleOut])
def read_event_schedules_by_event_id(event_id: UUID, db: Session = Depends(get_db)):
    schedules = get_event_schedules_by_event_id(db, event_id)
    if not schedules:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No schedules found for this event")
    return schedules

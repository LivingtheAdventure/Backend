from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from special.schema.schema import (
    CreateBestOFTheYear, CreateUpcommingEvent,
    BestOFTheYearOut, UpcommingEventsOut
)
from special.service import service
from database.database import get_db  # make sure this is defined properly

router = APIRouter(prefix="/special", tags=["Special Events"])

# -------------------- Best of the Year --------------------
@router.get("/best-of-the-year", response_model=list[BestOFTheYearOut])
def get_best_of_the_year(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return service.get_best_of_the_year(db, skip, limit)

@router.get("/best_of_the_year/uuid/{uuid}", response_model=BestOFTheYearOut)
def read_best_of_the_year_by_uuid(uuid: str, db: Session = Depends(get_db)):
    data = service.get_best_of_the_year_by_uuid(db, uuid)
    if not data:
        raise HTTPException(status_code=404, detail="Not found")
    return data

@router.post("/best-of-the-year", response_model=BestOFTheYearOut)
def create_best_of_the_year(payload: CreateBestOFTheYear, db: Session = Depends(get_db)):
    return service.create_best_of_the_year(db, event_id=payload.event, status=payload.status)


@router.delete("/best-of-the-year/{id}", response_model=BestOFTheYearOut)
def delete_best_of_the_year(id: int, db: Session = Depends(get_db)):
    deleted = service.delete_best_of_the_year(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    return deleted


# -------------------- Upcoming Events --------------------
@router.get("/upcoming-events", response_model=list[UpcommingEventsOut])
def get_upcomming_events(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return service.get_upcomming_events(db, skip, limit)


@router.get("/upcoming_events/uuid/{uuid}", response_model=UpcommingEventsOut)
def read_upcoming_event_by_uuid(uuid: str, db: Session = Depends(get_db)):
    data = service.get_upcoming_event_by_uuid(db, uuid)
    if not data:
        raise HTTPException(status_code=404, detail="Not found")
    return data

@router.post("/upcoming-events", response_model=UpcommingEventsOut)
def create_upcomming_event(payload: CreateUpcommingEvent, db: Session = Depends(get_db)):
    return service.create_upcomming_event(db, event_id=payload.event, status=payload.status)


@router.delete("/upcoming-events/{id}", response_model=UpcommingEventsOut)
def delete_upcomming_event(id: int, db: Session = Depends(get_db)):
    deleted = service.delete_upcomming_event(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    return deleted

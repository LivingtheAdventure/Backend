from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from special.schema.schema import (
    CreateBestOFTheYear,
    CreateUpcommingEvent,
    BestOFTheYearOut,
    UpcommingEventsOut,
)

from special.service import service
from database.database import get_db
from admin.service.service import get_current_admin
from logs.service.service import create_user_action_log

router = APIRouter(
    prefix="/special",
    tags=["Special Events"],
)


# -------------------- Best of the Year --------------------


@router.get(
    "/best-of-the-year",
    response_model=list[BestOFTheYearOut],
)
def get_best_of_the_year(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return service.get_best_of_the_year(db, skip, limit)


@router.get(
    "/best_of_the_year/uuid/{uuid}",
    response_model=BestOFTheYearOut,
)
def read_best_of_the_year_by_uuid(
    uuid: str,
    db: Session = Depends(get_db),
):
    data = service.get_best_of_the_year_by_uuid(db, uuid)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )

    return data


@router.post(
    "/best-of-the-year",
    response_model=BestOFTheYearOut,
)
def create_best_of_the_year(
    payload: CreateBestOFTheYear,
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin),
):
    try:
        created = service.create_best_of_the_year(
            db,
            event_id=payload.event,
            status=payload.status,
        )

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="BEST_OF_THE_YEAR_CREATED",
            entity="BEST_OF_THE_YEAR",
            entity_id=str(created.id),
            description="Event was added to Best of the Year successfully",
        )

        return created

    except Exception:
        db.rollback()

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="BEST_OF_THE_YEAR_CREATED",
            entity="BEST_OF_THE_YEAR",
            description="Failed to add event to Best of the Year",
        )

        raise


@router.delete(
    "/best-of-the-year/{id}",
    response_model=BestOFTheYearOut,
)
def delete_best_of_the_year(
    id: int,
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin),
):
    try:
        deleted = service.delete_best_of_the_year(db, id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Record not found",
            )

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="BEST_OF_THE_YEAR_DELETED",
            entity="BEST_OF_THE_YEAR",
            entity_id=str(id),
            description="Event was removed from Best of the Year successfully",
        )

        return deleted

    except HTTPException:
        raise

    except Exception:
        db.rollback()

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="BEST_OF_THE_YEAR_DELETED",
            entity="BEST_OF_THE_YEAR",
            entity_id=str(id),
            description="Failed to remove event from Best of the Year",
        )

        raise


# -------------------- Upcoming Events --------------------


@router.get(
    "/upcoming-events",
    response_model=list[UpcommingEventsOut],
)
def get_upcomming_events(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return service.get_upcomming_events(db, skip, limit)


@router.get(
    "/upcoming_events/uuid/{uuid}",
    response_model=UpcommingEventsOut,
)
def read_upcoming_event_by_uuid(
    uuid: str,
    db: Session = Depends(get_db),
):
    data = service.get_upcoming_event_by_uuid(db, uuid)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )

    return data


@router.post(
    "/upcoming-events",
    response_model=UpcommingEventsOut,
)
def create_upcomming_event(
    payload: CreateUpcommingEvent,
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin),
):
    try:
        created = service.create_upcomming_event(
            db,
            event_id=payload.event,
            status=payload.status,
        )

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="UPCOMING_EVENT_CREATED",
            entity="UPCOMING_EVENT",
            entity_id=str(created.id),
            description="Event was added to Upcoming Events successfully",
        )

        return created

    except Exception:
        db.rollback()

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="UPCOMING_EVENT_CREATED",
            entity="UPCOMING_EVENT",
            description="Failed to add event to Upcoming Events",
        )

        raise


@router.delete(
    "/upcoming-events/{id}",
    response_model=UpcommingEventsOut,
)
def delete_upcomming_event(
    id: int,
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin),
):
    try:
        deleted = service.delete_upcomming_event(db, id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Record not found",
            )

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="UPCOMING_EVENT_DELETED",
            entity="UPCOMING_EVENT",
            entity_id=str(id),
            description="Event was removed from Upcoming Events successfully",
        )

        return deleted

    except HTTPException:
        raise

    except Exception:
        db.rollback()

        create_user_action_log(
            db=db,
            user_id=admin_id,
            action="UPCOMING_EVENT_DELETED",
            entity="UPCOMING_EVENT",
            entity_id=str(id),
            description="Failed to remove event from Upcoming Events",
        )

        raise

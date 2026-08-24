from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from authentication.service.service import firebase_auth_dep
from authentication.model.model import User
from database.database import get_db
from favourite.model.model import Favourite
from logs.service.service import create_user_action_log

router = APIRouter(prefix="/favourites", tags=["favourites"])


@router.get("/")
def list_my_favourites(
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    try:
        phone = decoded.get("phone_number")

        if not phone:
            return {"favourites": []}

        user = db.query(User).filter(User.phone == phone).first()

        if not user:
            return {"favourites": []}

        rows = db.query(Favourite).filter(Favourite.user_id == user.user_id).all()

        return {"favourites": [row.event_id for row in rows]}

    except Exception:
        # If anything fails, never break UI
        return {"favourites": []}


@router.post("/toggle")
def toggle_favourite(
    event_id: str,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    phone = decoded.get("phone_number")

    if not phone:
        return {"event_id": event_id, "is_favourite": False}

    user = db.query(User).filter(User.phone == phone).first()

    if not user:
        return {"event_id": event_id, "is_favourite": False}

    existing = (
        db.query(Favourite)
        .filter(Favourite.user_id == user.user_id, Favourite.event_id == event_id)
        .first()
    )

    # Remove from favourites
    if existing:
        try:
            db.delete(existing)
            db.commit()

            create_user_action_log(
                db=db,
                user_id=user.user_id,
                action="FAVOURITE_REMOVED",
                entity="EVENT",
                entity_id=str(event_id),
                description="Event was removed from favourites successfully",
            )

            return {"event_id": event_id, "is_favourite": False}

        except Exception:
            db.rollback()

            create_user_action_log(
                db=db,
                user_id=user.user_id,
                action="FAVOURITE_REMOVE_FAILED",
                entity="EVENT",
                entity_id=str(event_id),
                description="Failed to remove event from favourites",
            )

            return {"event_id": event_id, "is_favourite": True}

    # Add to favourites
    try:
        fav = Favourite(user_id=user.user_id, event_id=event_id)

        db.add(fav)
        db.commit()

        create_user_action_log(
            db=db,
            user_id=user.user_id,
            action="FAVOURITE_ADDED",
            entity="EVENT",
            entity_id=str(event_id),
            description="Event was added to favourites successfully",
        )

        return {"event_id": event_id, "is_favourite": True}

    except Exception:
        db.rollback()

        create_user_action_log(
            db=db,
            user_id=user.user_id,
            action="FAVOURITE_ADD_FAILED",
            entity="EVENT",
            entity_id=str(event_id),
            description="Failed to add event to favourites",
        )

        return {"event_id": event_id, "is_favourite": False}

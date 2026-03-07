from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from authentication.service.service import firebase_auth_dep
from authentication.model.model import User
from database.database import get_db
from favourite.model.model import Favourite

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

        rows = db.query(Favourite).filter(
            Favourite.user_id == user.user_id
        ).all()

        return {
            "favourites": [row.event_id for row in rows]
        }

    except Exception:
        # If anything fails, never break UI
        return {"favourites": []}


@router.post("/toggle")
def toggle_favourite(
    event_id: str,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    try:
        phone = decoded.get("phone_number")

        if not phone:
            return {"event_id": event_id, "is_favourite": False}

        user = db.query(User).filter(User.phone == phone).first()

        if not user:
            return {"event_id": event_id, "is_favourite": False}

        existing = db.query(Favourite).filter(
            Favourite.user_id == user.user_id,
            Favourite.event_id == event_id
        ).first()

        if existing:
            db.delete(existing)
            db.commit()

            return {
                "event_id": event_id,
                "is_favourite": False
            }

        fav = Favourite(
            user_id=user.user_id,
            event_id=event_id
        )

        db.add(fav)
        db.commit()

        return {
            "event_id": event_id,
            "is_favourite": True
        }

    except Exception:
        return {"event_id": event_id, "is_favourite": False}
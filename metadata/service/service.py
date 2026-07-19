from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from event.model.model import Event
from authentication.model.model import User
from datetime import datetime, timedelta
from sqlalchemy import func

def get_event_metadata(db: Session):

    now = datetime.utcnow()

    today = now.date()

    week_start = now - timedelta(days=7)

    month_start = now.replace(day=1)

    labels = dict(
        db.query(
            Event.label,
            func.count(Event.id)
        )
        .group_by(Event.label)
        .all()
    )

    latest = db.query(func.max(Event.updated_at)).scalar()

    return {

        "total_events":
            db.query(Event).count(),

        "published_events":
            db.query(Event).filter(
                Event.status == "published"
            ).count(),

        "draft_events":
            db.query(Event).filter(
                Event.status == "draft"
            ).count(),

        "archived_events":
            db.query(Event).filter(
                Event.status == "archived"
            ).count(),

        "upcoming_events":
            db.query(Event).filter(
                Event.state == "Upcoming"
            ).count(),

        "completed_events":
            db.query(Event).filter(
                Event.state == "Completed"
            ).count(),

        "in_progress_events":
            db.query(Event).filter(
                Event.state == "In Progress"
            ).count(),

        "sold_out_events":
            db.query(Event).filter(
                Event.state == "Sold Out"
            ).count(),

        "trek_events":
            db.query(Event).filter(
                Event.event_type == "trek"
            ).count(),

        "trip_events":
            db.query(Event).filter(
                Event.event_type == "trip"
            ).count(),

        "adventure_events":
            db.query(Event).filter(
                Event.event_type == "adventure"
            ).count(),

        "peak_events":
            db.query(Event).filter(
                Event.event_type == "peak"
            ).count(),

        "special_events":
            db.query(Event).filter(
                Event.event_type == "special_event"
            ).count(),

        "labels": labels,

        "created_today":
            db.query(Event).filter(
                func.date(Event.created_at) == today
            ).count(),

        "created_this_week":
            db.query(Event).filter(
                Event.created_at >= week_start
            ).count(),

        "created_this_month":
            db.query(Event).filter(
                Event.created_at >= month_start
            ).count(),

        "last_updated": latest
    }

    
def get_user_metadata(db: Session):

    now = datetime.utcnow()

    today = now.date()

    week_start = now - timedelta(days=7)

    month_start = now.replace(day=1)

    return {

        "total_users":
            db.query(User).count(),

        "active_users":
            db.query(User)
            .filter(User.is_active == True)
            .count(),

        "inactive_users":
            db.query(User)
            .filter(User.is_active == False)
            .count(),

        "verified_users":
            db.query(User)
            .filter(User.is_verified == True)
            .count(),

        "unverified_users":
            db.query(User)
            .filter(User.is_verified == False)
            .count(),

        "users_with_email":
            db.query(User)
            .filter(User.email.isnot(None))
            .count(),

        "users_without_email":
            db.query(User)
            .filter(User.email.is_(None))
            .count(),

        "new_users_today":
            db.query(User)
            .filter(
                func.date(User.created_at) == today
            )
            .count(),

        "new_users_this_week":
            db.query(User)
            .filter(
                User.created_at >= week_start
            )
            .count(),

        "new_users_this_month":
            db.query(User)
            .filter(
                User.created_at >= month_start
            )
            .count(),
    }
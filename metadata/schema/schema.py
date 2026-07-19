from datetime import datetime
from pydantic import BaseModel
from typing import Dict


class EventMetadataOut(BaseModel):

    total_events: int

    published_events: int
    draft_events: int
    archived_events: int

    upcoming_events: int
    completed_events: int
    in_progress_events: int
    sold_out_events: int

    trek_events: int
    trip_events: int
    adventure_events: int
    peak_events: int
    special_events: int

    labels: Dict[str, int]

    created_today: int
    created_this_week: int
    created_this_month: int

    last_updated: datetime | None


class UserMetadataOut(BaseModel):

    total_users: int

    active_users: int
    inactive_users: int

    verified_users: int
    unverified_users: int

    users_with_email: int
    users_without_email: int

    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
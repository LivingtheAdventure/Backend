from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from admin.service.service import get_current_admin

from metadata.service.service import get_event_metadata,get_user_metadata
from metadata.schema.schema import EventMetadataOut, UserMetadataOut

router = APIRouter(
    prefix="/metadata",
    tags=["Metadata"]
)

@router.get(
    "/events",
    response_model=EventMetadataOut
)
def read_event_metadata(
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin)
):
    return get_event_metadata(db)

@router.get(
    "/users",
    response_model=UserMetadataOut,
)
def read_user_metadata(
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin),
):
    return get_user_metadata(db)
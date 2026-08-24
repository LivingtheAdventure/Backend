from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from logs.model.model import SystemLogs


def create_user_action_log(
    db: Session,
    user_id: UUID,
    action: str,
    entity: Optional[str] = None,
    entity_id: Optional[str] = None,
    description: Optional[str] = None,
    extra_data: Optional[dict] = None,
):
    log = SystemLogs(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        description=description,
        extra_data=extra_data,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log

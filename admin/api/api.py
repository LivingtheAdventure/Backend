from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from logs.service.service import create_user_action_log

from admin.schema.schema import AdminLoginRequest, AdminLoginResponse

from admin.service.service import (
    authenticate_admin,
    create_access_token,
    get_current_admin,
)

router = APIRouter(prefix="/admin", tags=["admin"])


# LOGIN
@router.post("/login", response_model=AdminLoginResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    try:
        admin = authenticate_admin(db, payload.email, payload.password)

        token = create_access_token({"admin_id": admin.admin_id})

        create_user_action_log(
            db=db,
            user_id=admin.admin_id,
            action="ADMIN_LOGIN",
            entity="ADMIN",
            entity_id=str(admin.admin_id),
            description="Admin logged in successfully",
        )

        return {"access_token": token}

    except Exception:
        db.rollback()

        # We may not have a valid admin_id when authentication fails,
        # so don't create a user-action log in that case.

        raise


# PROTECTED TEST ROUTE
@router.get("/me")
def get_admin_me(
    admin_id=Depends(get_current_admin),
):
    return {"admin_id": admin_id}

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from authentication.service.service import firebase_auth_dep
from admin.service.service import get_current_admin

from payment.schema.schema import (
    CreateOrderRequest,
    CreateOrderResponse,
    VerifyPaymentRequest,
    PaymentDetailsResponse,
    AdminBookingListResponse,
)

from payment.service.service import (
    create_payment_order,
    verify_payment,
    get_payment_details,
    get_all_bookings,
)

from logs.service.service import create_user_action_log

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


# ============================================================
# CREATE PAYMENT ORDER
# ============================================================


@router.post(
    "/create-order",
    response_model=CreateOrderResponse,
)
def create_order(
    payload: CreateOrderRequest,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    try:
        result = create_payment_order(
            payload=payload,
            decoded=decoded,
            db=db,
        )

        phone = decoded.get("phone_number")

        if phone:
            from authentication.model.model import User

            user = db.query(User).filter(User.phone == phone).first()

            if user:
                create_user_action_log(
                    db=db,
                    user_id=user.user_id,
                    action="PAYMENT_ORDER_CREATED",
                    entity="PAYMENT",
                    description="Payment order was created successfully",
                )

        return result

    except Exception:
        db.rollback()

        phone = decoded.get("phone_number")

        if phone:
            from authentication.model.model import User

            user = db.query(User).filter(User.phone == phone).first()

            if user:
                create_user_action_log(
                    db=db,
                    user_id=user.user_id,
                    action="PAYMENT_ORDER_CREATED",
                    entity="PAYMENT",
                    description="Failed to create payment order",
                )

        raise


# ============================================================
# VERIFY PAYMENT
# ============================================================


@router.post(
    "/verify",
)
def verify(
    payload: VerifyPaymentRequest,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    try:
        result = verify_payment(
            payload=payload,
            decoded=decoded,
            db=db,
        )

        phone = decoded.get("phone_number")

        if phone:
            from authentication.model.model import User

            user = db.query(User).filter(User.phone == phone).first()

            if user:
                create_user_action_log(
                    db=db,
                    user_id=user.user_id,
                    action="PAYMENT_VERIFIED",
                    entity="PAYMENT",
                    description="Payment was verified successfully",
                )

        return result

    except Exception:
        db.rollback()

        phone = decoded.get("phone_number")

        if phone:
            from authentication.model.model import User

            user = db.query(User).filter(User.phone == phone).first()

            if user:
                create_user_action_log(
                    db=db,
                    user_id=user.user_id,
                    action="PAYMENT_VERIFIED",
                    entity="PAYMENT",
                    description="Payment verification failed",
                )

        raise


# ============================================================
# ADMIN - GET ALL BOOKINGS
# ============================================================


@router.get(
    "/get-all-bookings",
    response_model=AdminBookingListResponse,
)
def list_all_bookings(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    booking_status: str | None = Query(
        None,
        description="Filter by booking status",
    ),
    payment_status: str | None = Query(
        None,
        description="Filter by payment status",
    ),
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin),
):
    return get_all_bookings(
        db=db,
        page=page,
        limit=limit,
        booking_status=booking_status,
        payment_status=payment_status,
    )


# ============================================================
# USER - GET PAYMENT DETAILS
# ============================================================


@router.get(
    "/{booking_id}",
    response_model=PaymentDetailsResponse,
)
def payment_details(
    booking_id: str,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    return get_payment_details(
        booking_id=booking_id,
        decoded=decoded,
        db=db,
    )

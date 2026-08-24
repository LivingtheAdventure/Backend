from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from database.database import get_db

from authentication.service.service import firebase_auth_dep

from payment.schema.schema import (
    CreateOrderRequest,
    CreateOrderResponse,
    VerifyPaymentRequest,
    PaymentDetailsResponse,
)

from payment.service.service import (
    create_payment_order,
    verify_payment,
    get_payment_details,
)

from logs.service.service import create_user_action_log

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


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

        # Get user from decoded Firebase information if available.
        # Adjust this depending on how your payment service identifies the user.
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

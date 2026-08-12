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
    return create_payment_order(
        payload=payload,
        decoded=decoded,
        db=db,
    )


@router.post(
    "/verify",
)
def verify(
    payload: VerifyPaymentRequest,
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):
    return verify_payment(
        payload=payload,
        decoded=decoded,
        db=db,
    )


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

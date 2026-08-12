from fastapi import HTTPException
from sqlalchemy.orm import Session

from authentication.model.model import User
from event.model.model import Event
from schedule.model.model import EventSchedule

from payment.model.Booking import Booking
from payment.model.Payment import Payment
from sqlalchemy.sql import func

from payment.razorpay_client import razorpay_client, RAZORPAY_KEY_ID

from payment.utils.utils import (
    find_pickup,
    validate_capacity,
    calculate_subtotal,
    find_best_discount,
    calculate_discount,
    calculate_final_amount,
)


def get_current_user(
    decoded: dict,
    db: Session,
) -> User:
    """
    Get authenticated user from Firebase decoded token.
    """

    phone = decoded.get("phone_number")

    if not phone:
        raise HTTPException(
            status_code=401,
            detail="Authenticated phone number not found.",
        )

    user = db.query(User).filter(User.phone == phone).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return user


def create_payment_order(
    payload,
    decoded: dict,
    db: Session,
):
    user = get_current_user(decoded, db)

    # ---------------------------------------------------------
    # 1. Find Event
    # ---------------------------------------------------------

    event = db.query(Event).filter(Event.event_id == payload.event_id).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found.",
        )

    # ---------------------------------------------------------
    # 2. Find Schedule
    # ---------------------------------------------------------

    schedule = (
        db.query(EventSchedule)
        .filter(
            EventSchedule.schedule_id == payload.schedule_id,
            EventSchedule.event_id == payload.event_id,
        )
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail="Schedule not found for this event.",
        )

    # ---------------------------------------------------------
    # 3. Check schedule status
    # ---------------------------------------------------------

    if schedule.status and schedule.status.lower() != "active":
        raise HTTPException(
            status_code=400,
            detail="This schedule is not available for booking.",
        )

    schedule_data = schedule.schedule_data or {}

    # ---------------------------------------------------------
    # 4. Validate capacity
    # ---------------------------------------------------------

    validate_capacity(
        schedule_data,
        payload.number_of_people,
    )

    # ---------------------------------------------------------
    # 5. Find selected pickup
    # ---------------------------------------------------------

    pickup = find_pickup(
        schedule_data,
        payload.pickup_uuid,
    )

    # ---------------------------------------------------------
    # 6. Get price
    # ---------------------------------------------------------

    price_per_person = float(pickup.get("price_per_person", 0))

    if price_per_person <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid price configured for this pickup.",
        )

    # ---------------------------------------------------------
    # 7. Calculate subtotal
    # ---------------------------------------------------------

    subtotal = calculate_subtotal(
        price_per_person,
        payload.number_of_people,
    )

    # ---------------------------------------------------------
    # 8. Find applicable discount
    # ---------------------------------------------------------

    discount = find_best_discount(
        pickup.get("discounts", []),
        payload.number_of_people,
    )

    # ---------------------------------------------------------
    # 9. Calculate discount
    # ---------------------------------------------------------

    discount_amount = calculate_discount(
        subtotal=subtotal,
        price_per_person=price_per_person,
        people=payload.number_of_people,
        discount=discount,
    )

    # ---------------------------------------------------------
    # 10. Calculate final amount
    # ---------------------------------------------------------

    final_amount = calculate_final_amount(
        subtotal,
        discount_amount,
    )

    # ---------------------------------------------------------
    # 11. Create Booking
    # ---------------------------------------------------------

    booking = Booking(
        user_id=user.user_id,
        event_id=payload.event_id,
        schedule_id=payload.schedule_id,
        pickup_uuid=payload.pickup_uuid,
        number_of_people=payload.number_of_people,
        price_per_person=price_per_person,
        subtotal=subtotal,
        discount_label=(discount.get("label") if discount else None),
        discount_type=(discount.get("type") if discount else None),
        discount_scope=(discount.get("scope") if discount else None),
        discount_value=(float(discount.get("value", 0)) if discount else None),
        discount_amount=discount_amount,
        final_amount=final_amount,
        currency="INR",
        booking_status="PENDING",
    )

    db.add(booking)
    db.flush()

    # ---------------------------------------------------------
    # 12. Create Razorpay order
    # ---------------------------------------------------------

    amount_in_paise = int(round(final_amount * 100))

    if amount_in_paise <= 0:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Invalid payment amount.",
        )

    try:

        razorpay_order = razorpay_client.order.create(
            {
                "amount": amount_in_paise,
                "currency": "INR",
                "receipt": str(booking.booking_id),
            }
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=502,
            detail="Unable to create Razorpay order.",
        ) from exc

    # ---------------------------------------------------------
    # 13. Create Payment
    # ---------------------------------------------------------

    payment = Payment(
        booking_id=booking.booking_id,
        razorpay_order_id=razorpay_order["id"],
        amount_paid=final_amount,
        payment_status="PENDING",
    )

    db.add(payment)

    # ---------------------------------------------------------
    # 14. Commit
    # ---------------------------------------------------------

    try:

        db.commit()

        db.refresh(booking)
        db.refresh(payment)

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to save payment information.",
        ) from exc

    # ---------------------------------------------------------
    # 15. Return checkout information
    # ---------------------------------------------------------

    return {
        "booking_id": booking.booking_id,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key": RAZORPAY_KEY_ID,
        "amount": amount_in_paise,
        "currency": "INR",
        "number_of_people": booking.number_of_people,
        "final_amount": booking.final_amount,
    }


def verify_payment(
    payload,
    decoded: dict,
    db: Session,
):
    user = get_current_user(decoded, db)

    # ---------------------------------------------------------
    # 1. Find booking owned by current user
    # ---------------------------------------------------------

    booking = (
        db.query(Booking)
        .filter(
            Booking.booking_id == payload.booking_id,
            Booking.user_id == user.user_id,
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )

    # ---------------------------------------------------------
    # 2. Find payment
    # ---------------------------------------------------------

    payment = db.query(Payment).filter(Payment.booking_id == booking.booking_id).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment record not found.",
        )

    # ---------------------------------------------------------
    # 3. Make sure Razorpay order matches
    # ---------------------------------------------------------

    if payment.razorpay_order_id != payload.razorpay_order_id:
        raise HTTPException(
            status_code=400,
            detail="Razorpay order does not match booking.",
        )

    # ---------------------------------------------------------
    # 4. Prevent duplicate verification
    # ---------------------------------------------------------

    if payment.payment_status == "SUCCESS":

        return {
            "success": True,
            "booking_id": booking.booking_id,
            "payment_status": "SUCCESS",
            "booking_status": booking.booking_status,
        }

    # ---------------------------------------------------------
    # 5. Verify Razorpay signature
    # ---------------------------------------------------------

    verification_data = {
        "razorpay_order_id": payload.razorpay_order_id,
        "razorpay_payment_id": payload.razorpay_payment_id,
        "razorpay_signature": payload.razorpay_signature,
    }

    try:

        razorpay_client.utility.verify_payment_signature(verification_data)

    except Exception as exc:

        payment.payment_status = "FAILED"

        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Payment verification failed.",
        ) from exc

    # ---------------------------------------------------------
    # 6. Payment successful
    # ---------------------------------------------------------

    payment.razorpay_payment_id = payload.razorpay_payment_id

    payment.razorpay_signature = payload.razorpay_signature

    payment.payment_status = "SUCCESS"

    # We know this payment belongs to this booking.
    payment.amount_paid = booking.final_amount

    payment.paid_at = func.now()

    # ---------------------------------------------------------
    # 7. Confirm booking
    # ---------------------------------------------------------

    booking.booking_status = "CONFIRMED"

    try:

        db.commit()

        db.refresh(payment)
        db.refresh(booking)

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Payment verified but booking update failed.",
        ) from exc

    return {
        "success": True,
        "booking_id": booking.booking_id,
        "payment_status": payment.payment_status,
        "booking_status": booking.booking_status,
    }


def get_payment_details(
    booking_id,
    decoded: dict,
    db: Session,
):
    user = get_current_user(decoded, db)

    booking = (
        db.query(Booking)
        .filter(
            Booking.booking_id == booking_id,
            Booking.user_id == user.user_id,
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )

    payment = db.query(Payment).filter(Payment.booking_id == booking.booking_id).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found.",
        )

    return {
        "booking_id": booking.booking_id,
        "event_id": booking.event_id,
        "payment_status": payment.payment_status,
        "booking_status": booking.booking_status,
        "amount": booking.final_amount,
        "number_of_people": booking.number_of_people,
    }

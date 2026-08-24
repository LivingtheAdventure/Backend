from pydantic import BaseModel, UUID4, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID


class CreateOrderRequest(BaseModel):
    event_id: UUID4
    schedule_id: UUID4
    pickup_uuid: str
    number_of_people: int = Field(gt=0, le=20)


class CreateOrderResponse(BaseModel):
    booking_id: UUID4
    razorpay_order_id: str
    razorpay_key: str
    amount: int
    currency: str
    number_of_people: int
    final_amount: float


class VerifyPaymentRequest(BaseModel):
    booking_id: UUID4
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentDetailsResponse(BaseModel):
    booking_id: UUID4
    event_id: UUID4
    payment_status: str
    booking_status: str
    amount: float
    number_of_people: int


class AdminBookingOut(BaseModel):
    booking_id: UUID

    user_id: UUID
    event_id: UUID
    schedule_id: UUID

    pickup_uuid: str

    number_of_people: int

    price_per_person: float
    subtotal: float

    discount_label: Optional[str] = None
    discount_type: Optional[str] = None
    discount_scope: Optional[str] = None
    discount_value: Optional[float] = None
    discount_amount: Optional[float] = None

    final_amount: float
    currency: str

    booking_status: str

    payment_status: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AdminBookingListResponse(BaseModel):
    total: int
    page: int
    limit: int
    bookings: list[AdminBookingOut]

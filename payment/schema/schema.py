from pydantic import BaseModel, UUID4, Field


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

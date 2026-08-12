import uuid

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from database.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    payment_id = Column(
        PG_UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    booking_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )

    razorpay_order_id = Column(
        String,
        unique=True,
        nullable=True,
    )

    razorpay_payment_id = Column(
        String,
        unique=True,
        nullable=True,
    )

    razorpay_signature = Column(
        String,
        nullable=True,
    )

    payment_method = Column(
        String,
        nullable=True,
    )

    amount_paid = Column(
        Float,
        nullable=False,
    )

    payment_status = Column(
        String,
        default="PENDING",
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=False),
        server_default=func.now(),
    )

    paid_at = Column(
        DateTime(timezone=False),
        nullable=True,
    )

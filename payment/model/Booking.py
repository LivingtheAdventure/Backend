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


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(
        PG_UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    user_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )

    event_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )

    schedule_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )

    # This comes from your schedule JSON
    pickup_uuid = Column(
        String,
        nullable=False,
    )

    number_of_people = Column(
        Integer,
        nullable=False,
    )

    price_per_person = Column(
        Float,
        nullable=False,
    )

    subtotal = Column(
        Float,
        nullable=False,
    )

    # Discount Information
    discount_label = Column(
        String,
        nullable=True,
    )

    discount_type = Column(
        String,
        nullable=True,
    )

    discount_scope = Column(
        String,
        nullable=True,
    )

    discount_value = Column(
        Float,
        nullable=True,
    )

    discount_amount = Column(
        Float,
        nullable=True,
    )

    final_amount = Column(
        Float,
        nullable=False,
    )

    currency = Column(
        String,
        default="INR",
        nullable=False,
    )

    booking_status = Column(
        String,
        default="PENDING",
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=False),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
    )

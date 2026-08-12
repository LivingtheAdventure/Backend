from fastapi import HTTPException


def find_pickup(schedule_data: dict, pickup_uuid: str) -> dict:
    """
    Returns the selected pickup object from schedule_data.
    """

    pickups = schedule_data.get("pickups", [])

    pickup = next(
        (item for item in pickups if item.get("pickup_uuid") == pickup_uuid),
        None,
    )

    if pickup is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid pickup selected.",
        )

    return pickup


def calculate_subtotal(
    price_per_person: float,
    number_of_people: int,
) -> float:
    return price_per_person * number_of_people


def find_best_discount(
    discounts: list,
    number_of_people: int,
):
    """
    Returns the best applicable discount.
    """

    applicable = [
        discount
        for discount in discounts
        if number_of_people >= discount.get("min_group_size", 1)
    ]

    if not applicable:
        return None

    return max(
        applicable,
        key=lambda d: d.get("value", 0),
    )


def calculate_discount(
    subtotal: float,
    price_per_person: float,
    people: int,
    discount: dict | None,
):
    if discount is None:
        return 0

    value = discount["value"]

    if discount["type"] == "percentage":

        if discount["scope"] == "per_person":
            return price_per_person * people * value / 100

        return subtotal * value / 100

    if discount["type"] == "fixed":

        if discount["scope"] == "per_person":
            return value * people

        return value

    return 0


def calculate_final_amount(
    subtotal: float,
    discount_amount: float,
) -> float:

    return max(
        subtotal - discount_amount,
        0,
    )


def validate_capacity(
    schedule_data: dict,
    requested_people: int,
):
    capacity = schedule_data.get(
        "capacity_pricing",
        {},
    )

    available = capacity.get(
        "seats_available",
        0,
    )

    if requested_people > available:
        raise HTTPException(
            status_code=400,
            detail="Not enough seats available.",
        )

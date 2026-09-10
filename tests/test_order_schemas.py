"""
test_order_schemas.py
"""
import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.order import OrderCreate, OrderCreateWithItems, OrderRead, OrderUpdate


def test_empty_update_order_schema():
    order_update = OrderUpdate()

    update_data = order_update.model_dump(exclude_unset=True)

    assert update_data == {}


def test_partial_update_order_schema():
    order_update = OrderUpdate(title="Updated")

    update_data = order_update.model_dump(exclude_unset=True)

    assert update_data == {"title": "Updated"}


def test_null_update_order_schema():
    with pytest.raises(ValidationError):
        OrderUpdate(title=None)


def test_invalid_status_update_order_schema():
    with pytest.raises(ValidationError):
        OrderUpdate(status="unknown")


def test_valid_status_update_order_schema():
    order_update = OrderUpdate(status="canceled")
    update_data = order_update.model_dump(exclude_unset=True)

    assert update_data == {"status": "canceled"}


def test_strip_whitespaces_order_create_schema():
    create_order = OrderCreate(title=" space space ")
    created_data = create_order.model_dump()

    assert created_data == {"title": "space space"}


def test_whitespaces_only_order_create_schema():
    with pytest.raises(ValidationError):
        OrderCreate(title="  ")


def test_empty_title_order_create_schema():
    with pytest.raises(ValidationError):
        OrderCreate(title="")


def test_over_length_order_create_schema():
    title_over_length = "a" * 256

    with pytest.raises(ValidationError):
        OrderCreate(title=title_over_length)


def test_max_length_order_create_schema():
    title_max_length = "a" * 255
    create_order = OrderCreate(title=title_max_length)
    created_data = create_order.model_dump()

    assert created_data == {"title": title_max_length}


def test_strip_whitespaces_update_schema():
    update_order = OrderUpdate(title=" space space ")
    update_data = update_order.model_dump(exclude_unset=True)

    assert update_data == {"title": "space space"}


def test_whitespace_only_update_schema():
    with pytest.raises(ValidationError):
        OrderUpdate(title="  ")


def test_over_length_update_schema():
    title_over_length = "a" * 256

    with pytest.raises(ValidationError):
        OrderUpdate(title=title_over_length)


def test_max_length_update_schema():
    title_max_length = "a" * 255

    update_order = OrderUpdate(title=title_max_length)
    updated_data = update_order.model_dump(exclude_unset=True)

    assert updated_data == {"title": title_max_length}


def test_valid_status_read_schema():
    read_order = OrderRead(
        id=1,
        title="Test order",
        status="processing",
        created_at=datetime.datetime.now(datetime.UTC),
    )
    assert read_order.status == "processing"


def test_invalid_status_read_schema():
    with pytest.raises(ValidationError):
        OrderRead(
            id=1,
            title="Test order",
            status="cool",
            created_at=datetime.datetime.now(datetime.UTC),
        )


def test_valid_order_create_with_items():
    list_of_valid_items = [
        {
            "product_name": "Valid Item",
            "quantity": 1,
            "unit_price": "10.00"
        }
    ]
    create_order_with_items = OrderCreateWithItems.model_validate(
        {
            "title": "Valid order with items",
            "items": list_of_valid_items,
        }
    )

    assert create_order_with_items.title == "Valid order with items"
    assert len(create_order_with_items.items) == 1
    assert create_order_with_items.items[0].product_name == "Valid Item"
    assert create_order_with_items.items[0].quantity == 1
    assert create_order_with_items.items[0].unit_price == Decimal("10.00")


def test_empty_order_create_with_items():
    empty_list_o_items = []

    with pytest.raises(ValidationError):
        OrderCreateWithItems.model_validate(
            {
                "title": "Invalid order with empty items",
                "items": empty_list_o_items,
            }
        )

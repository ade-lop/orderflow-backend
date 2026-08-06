"""
test_order_schemas.py
"""
import datetime

import pytest
from pydantic import ValidationError

from app.schemas.order import OrderCreate, OrderRead, OrderUpdate


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

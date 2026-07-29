"""
test_order_schemas.py
"""
import pytest
from pydantic import ValidationError

from app.schemas.order import OrderUpdate


def test_empty_update_order_schema():
    order_update = OrderUpdate()

    update_data = order_update.model_dump(exclude_unset=True)

    assert update_data == {}


def test_partlial_update_order_schema():
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

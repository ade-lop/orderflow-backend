"""tests/test_order_item_schemas.py"""
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.order_item import OrderItem
from app.schemas.order_item import OrderItemCreate, OrderItemRead


def test_order_item_create_schema() -> None:
    order = OrderItemCreate(
        product_name=" Keyboard ",
        quantity=2,
        unit_price="199.99",
    )

    assert order.product_name == "Keyboard"
    assert order.quantity == 2
    assert order.unit_price == Decimal("199.99")


def test_invalid_quantity_order_item_create_schema() -> None:
    with pytest.raises(ValidationError):
        OrderItemCreate(
            product_name="new product",
            quantity=0,
            unit_price="100",
        )


def test_invalid_unit_price_order_item_create_schema() -> None:
    with pytest.raises(ValidationError):
        OrderItemCreate(
            product_name="product",
            quantity=1,
            unit_price=0,
        )


def test_empty_product_name_order_item_create_schema() -> None:
    with pytest.raises(ValidationError):
        OrderItemCreate(
            product_name="",
            quantity=1,
            unit_price=10,
        )


def test_over_decimal_places_order_item_create_schema() -> None:
    with pytest.raises(ValidationError):
        OrderItemCreate(
            product_name="prod",
            quantity=1,
            unit_price="10.123",
        )


def test_over_max_digits_order_item_create_schema() -> None:
    with pytest.raises(ValidationError):
        OrderItemCreate(
            product_name="prod",
            quantity=1,
            unit_price="12345678901.01",
        )


def test_order_item_read_schema() -> None:
    order_item = OrderItem(
        id=10,
        order_id=5,
        product_name="Product",
        quantity=10,
        unit_price=Decimal("999.99"),
    )
    read_order_item = OrderItemRead.model_validate(order_item)
    assert order_item.id == read_order_item.id
    assert order_item.order_id == read_order_item.order_id
    assert order_item.product_name == read_order_item.product_name
    assert order_item.quantity == read_order_item.quantity
    assert order_item.unit_price == read_order_item.unit_price

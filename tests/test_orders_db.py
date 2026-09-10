"""
tests/test_orders_db.py
Это уже integration test.
Зависит от db и примененных миграций.

доказывает, что:
- ORM model создаётся,
- engine подключается к PostgreSQL,
- миграция реально создала таблицу,
- INSERT проходит,
- server defaults работают,
- SELECT по primary key работает,
- cleanup откатывает outer_transaction
"""
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.exc import DataError, IntegrityError, PendingRollbackError

from app.models.order import Order
from app.models.order_item import OrderItem


def test_create_and_read_order(db_session):
    test_session_db = db_session

    test_order = Order(title="new_test_order")

    test_session_db.add(test_order)
    test_session_db.commit()
    test_session_db.refresh(test_order)

    created_order_id = test_order.id

    order_from_db = test_session_db.get(Order, created_order_id)

    assert order_from_db is not None
    assert order_from_db.title == "new_test_order"
    assert order_from_db.status == "new"
    assert order_from_db.created_at is not None


def test_invalid_status(db_session):
    db = db_session

    invalid_order = Order(title="Valid title", status="cool")
    db.add(invalid_order)

    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()

    valid_order = Order(title="Valid title", status="new")
    db.add(valid_order)
    db.flush()

    assert valid_order.id is not None


def test_empty_title(db_session):
    db = db_session

    invalid_order = Order(title="")
    db.add(invalid_order)

    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()


def test_bound_whitespaces_title(db_session):
    db = db_session

    invalid_order = Order(title=" title ")
    db.add(invalid_order)

    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()


def test_overlength_title(db_session):
    db = db_session

    over_length_title = "a" * 256

    invalid_order = Order(title=over_length_title)
    db.add(invalid_order)

    with pytest.raises(DataError):
        db.flush()

    db.rollback()


def test_failed_session_create_order_with_items(db_session):
    db = db_session

    order = Order(title="Order failed session M10")
    db.add(order)
    db.flush()

    order_id = order.id

    order_item = OrderItem(
        order_id=order_id,
        product_name="item A",
        quantity=0,
        unit_price=Decimal("20.00"),
    )
    db.add(order_item)

    with pytest.raises(IntegrityError):
        db.flush()

    with pytest.raises(PendingRollbackError):
        db.execute(select(Order))

    db.rollback()
    result = db.execute(
        select(Order)
        .where(Order.title == "Order failed session M10")
    )
    assert result.scalar_one_or_none() is None

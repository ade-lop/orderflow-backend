"""
tests/test_orders_db.py
Это уже integration test.
Зависит от db и примененных миграций.

доказывает, что:
- ORM model создаётся,
- SessionLocal работает,
- engine подключается к PostgreSQL,
- миграция реально создала таблицу,
- INSERT проходит,
- server defaults работают,
- SELECT по primary key работает,
- cleanup удаляет тестовую запись.
"""
import pytest
from sqlalchemy.exc import DataError, IntegrityError

from app.models.order import Order


def test_create_and_read_order(db_session):
    test_session_db, created_ids = db_session

    test_order = Order(title="new_test_order")

    test_session_db.add(test_order)
    test_session_db.commit()
    test_session_db.refresh(test_order)

    created_order_id = test_order.id
    created_ids.append(created_order_id)

    order_from_db = test_session_db.get(Order, created_order_id)

    assert order_from_db is not None
    assert order_from_db.title == "new_test_order"
    assert order_from_db.status == "new"
    assert order_from_db.created_at is not None


def test_invalid_status(db_session):
    db, created_ids = db_session

    invalid_order = Order(title="Valid title", status="cool")
    db.add(invalid_order)

    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()

    valid_order = Order(title="Valid title", status="new")
    db.add(valid_order)
    db.flush()

    created_ids.append(valid_order.id)

    assert valid_order.id is not None


def test_empty_title(db_session):
    db, _ = db_session

    invalid_order = Order(title="")
    db.add(invalid_order)

    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()


def test_bound_whitespaces_title(db_session):
    db, _ = db_session

    invalid_order = Order(title=" title ")
    db.add(invalid_order)

    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()


def test_overlength_title(db_session):
    db, _ = db_session

    over_length_title = "a" * 256

    invalid_order = Order(title=over_length_title)
    db.add(invalid_order)

    with pytest.raises(DataError):
        db.flush()

    db.rollback()

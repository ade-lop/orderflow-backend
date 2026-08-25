"""
tests/test_order_items_db.py
integration test.
Зависит от db и примененных миграций.

доказывает, что:
- ORM model создаётся,
- engine подключается к PostgreSQL,
- миграция реально создала таблицу,
- cleanup откатывает outer_transaction
"""
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from app.models.order import Order
from app.models.order_item import OrderItem


def test_create_order_items(db_session) -> None:
    db = db_session

    order = Order(title="order with items")

    db.add(order)
    db.commit()
    db.refresh(order)

    order_id = order.id

    order_item_1 = OrderItem(
        order_id=order_id,
        product_name="order item 1",
        quantity=11,
        unit_price=100,
    )
    order_item_2 = OrderItem(
        order_id=order_id,
        product_name="order item 2",
        quantity=22,
        unit_price=200,
    )

    db.add(order_item_1)
    db.add(order_item_2)
    db.commit()
    db.refresh(order_item_1)
    db.refresh(order_item_2)

    created_item_1 = db.get(OrderItem, order_item_1.id)
    created_item_2 = db.get(OrderItem, order_item_2.id)

    assert created_item_1 is not None
    assert created_item_2 is not None

    assert created_item_1.order_id == order_id
    assert created_item_2.order_id == order_id

    assert len(order.items) == 2

    item_ids = [item.id for item in order.items]

    item_1_id = order_item_1.id
    item_2_id = order_item_2.id

    assert set(item_ids) == {item_1_id, item_2_id}

    db.expunge_all()

    order = db.get(Order, order_id)
    assert order is not None

    item_ids = [item.id for item in order.items]
    assert set(item_ids) == {item_1_id, item_2_id}

    db.expunge_all()
    order_item_1 = db.get(OrderItem, item_1_id)
    assert order_item_1 is not None
    assert order_item_1.order is not None
    assert order_item_1.order.id == order_id


def test_invalid_fk_order_items(db_session) -> None:
    db = db_session

    assert db.get(Order, 99999) is None

    order_item = OrderItem(
        order_id=99999,
        product_name="invalid fk order item",
        quantity=2,
        unit_price=200,
    )

    db.add(order_item)
    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()


def test_invalid_quantity_order_items(db_session) -> None:
    db = db_session

    order = Order(title="new order")
    db.add(order)
    db.commit()
    assert db.get(Order, order.id) is not None

    order_item = OrderItem(
        order_id=order.id,
        product_name="new prod name",
        quantity=0,
        unit_price=200,
    )
    db.add(order_item)
    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()


def test_invalid_unit_price_order_items(db_session) -> None:
    db = db_session

    order = Order(title="new order")
    db.add(order)
    db.commit()
    assert db.get(Order, order.id) is not None

    order_item = OrderItem(
        order_id=order.id,
        product_name="new prod name",
        quantity=2,
        unit_price=0,
    )
    db.add(order_item)
    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()


def test_empty_product_name_order_items(db_session) -> None:
    db = db_session

    order = Order(title="new order")
    db.add(order)
    db.commit()
    assert db.get(Order, order.id) is not None

    order_item = OrderItem(
        order_id=order.id,
        product_name="",
        quantity=2,
        unit_price=100,
    )
    db.add(order_item)
    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()


def test_nontrimmed_product_name_order_items(db_session) -> None:
    db = db_session

    order = Order(title="new order")
    db.add(order)
    db.commit()
    assert db.get(Order, order.id) is not None

    order_item = OrderItem(
        order_id=order.id,
        product_name=" Keyboard ",
        quantity=2,
        unit_price=100,
    )
    db.add(order_item)
    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()


def test_delete_cascade_order_items(db_session) -> None:
    db = db_session

    order = Order(title="new title")
    db.add(order)
    db.commit()

    order_item_1 = OrderItem(
        order_id=order.id,
        product_name="name 2",
        quantity=2,
        unit_price=200,
    )
    order_item_2 = OrderItem(
        order_id=order.id,
        product_name="name 1",
        quantity=4,
        unit_price=400,
    )
    db.add(order_item_1)
    db.add(order_item_2)
    db.commit()

    order_id = order.id
    item_1_id = order_item_1.id
    item_2_id = order_item_2.id

    db.expunge_all()

    order = db.get(Order, order_id)
    assert order is not None

    db.delete(order)
    db.flush()

    order = db.get(Order, order_id)
    order_item_1 = db.get(OrderItem, item_1_id)
    order_item_2 = db.get(OrderItem, item_2_id)

    assert order is None
    assert order_item_1 is None
    assert order_item_2 is None


def test_delete_orphan_order_items(db_session) -> None:
    db = db_session

    order = Order(title="new order")
    db.add(order)
    db.commit()

    order_item_1 = OrderItem(
        order_id=order.id,
        product_name="one",
        quantity=20,
        unit_price=100,
    )
    order_item_2 = OrderItem(
        order_id=order.id,
        product_name="two",
        quantity=23,
        unit_price=150,
    )
    db.add(order_item_1)
    db.add(order_item_2)
    db.commit()

    order_id = order.id
    item_id_1 = order_item_1.id
    item_id_2 = order_item_2.id

    db.expunge_all()

    order = db.get(Order, order_id)
    assert order is not None

    order_item_1 = db.get(OrderItem, item_id_1)
    order.items.remove(order_item_1)

    db.flush()

    assert db.get(Order, order_id)
    assert db.get(OrderItem, item_id_2)
    assert db.get(OrderItem, item_id_1) is None


def test_join_order_items(db_session) -> None:
    db = db_session

    order_a = Order(title="Order A")
    db.add(order_a)

    order_b = Order(title="Order B")
    db.add(order_b)

    db.commit()

    order_a_item_1 = OrderItem(
        order_id=order_a.id,
        product_name="Keyboard",
        quantity=1,
        unit_price=15,
    )
    db.add(order_a_item_1)

    order_a_item_2 = OrderItem(
        order_id=order_a.id,
        product_name="Mouse",
        quantity=1,
        unit_price=25,
    )
    db.add(order_a_item_2)

    order_a_item_3 = OrderItem(
        order_id=order_a.id,
        product_name="Keyboard",
        quantity=1,
        unit_price=15,
    )
    db.add(order_a_item_3)

    order_b_item = OrderItem(
        order_id=order_b.id,
        product_name="Monitor",
        quantity=1,
        unit_price=50,
    )
    db.add(order_b_item)

    db.commit()

    stmt = (
        select(Order)
        .distinct()
        .join(Order.items)
        .where(
            OrderItem.product_name == "Keyboard"
        )
    )

    result = db.execute(stmt)
    orders = result.scalars().all()

    assert len(orders) == 1
    assert orders[0].id == order_a.id


def test_outer_join_order_items(db_session) -> None:
    db = db_session

    order_a = Order(title="Order A")
    db.add(order_a)

    order_b = Order(title="Order B")
    db.add(order_b)

    db.commit()

    order_a_item = OrderItem(
        order_id=order_a.id,
        product_name="Keyboard",
        quantity=1,
        unit_price=20,
    )
    db.add(order_a_item)
    db.commit()

    stmt = (
        select(Order, OrderItem)
        .outerjoin(Order.items)
    )
    result = db.execute(stmt)
    rows = result.all()

    row_by_order_id = {
        order.id: item
        for order, item in rows
    }

    assert row_by_order_id[order_a.id] is not None
    assert row_by_order_id[order_b.id] is None


def test_lazy_loading_order_items(db_session) -> None:
    db = db_session

    order_a = Order(title="Order A")
    db.add(order_a)

    order_b = Order(title="Order B")
    db.add(order_b)

    db.commit()

    order_a_item_1 = OrderItem(
        order_id=order_a.id,
        product_name="Pen",
        quantity=1,
        unit_price=1,
    )
    db.add(order_a_item_1)

    order_a_item_2 = OrderItem(
        order_id=order_a.id,
        product_name="Notepad",
        quantity=1,
        unit_price=15,
    )
    db.add(order_a_item_2)

    order_b_item_1 = OrderItem(
        order_id=order_b.id,
        product_name="Mouse",
        quantity=1,
        unit_price=200,
    )
    db.add(order_b_item_1)

    order_b_item_2 = OrderItem(
        order_id=order_b.id,
        product_name="Pen",
        quantity=1,
        unit_price=2,
    )
    db.add(order_b_item_2)
    db.commit()

    order_a_id = order_a.id
    order_b_id = order_b.id

    db.expunge_all()

    stmt = (
        select(Order)
    )
    result = db.execute(stmt)
    orders = result.scalars().all()

    assert len(orders) == 2
    assert {order.id for order in orders} == {order_a_id, order_b_id}

    order_by_id = {
        order.id: order
        for order in orders
    }
    assert {
        item.product_name
        for item in order_by_id[order_a_id].items
    } == {"Pen", "Notepad"}
    assert {
        item.product_name
        for item in order_by_id[order_b_id].items
    } == {"Mouse", "Pen"}


def test_selectin_loading_order_items(db_session) -> None:
    db = db_session

    order_a = Order(title="Order A")
    db.add(order_a)

    order_b = Order(title="Order B")
    db.add(order_b)

    db.commit()

    order_a_item_1 = OrderItem(
        order_id=order_a.id,
        product_name="Pen",
        quantity=1,
        unit_price=1,
    )
    db.add(order_a_item_1)

    order_a_item_2 = OrderItem(
        order_id=order_a.id,
        product_name="Notepad",
        quantity=1,
        unit_price=15,
    )
    db.add(order_a_item_2)

    order_b_item_1 = OrderItem(
        order_id=order_b.id,
        product_name="Mouse",
        quantity=1,
        unit_price=200,
    )
    db.add(order_b_item_1)

    order_b_item_2 = OrderItem(
        order_id=order_b.id,
        product_name="Pen",
        quantity=1,
        unit_price=2,
    )
    db.add(order_b_item_2)
    db.commit()

    order_a_id = order_a.id
    order_b_id = order_b.id

    db.expunge_all()

    stmt = (
        select(Order)
        .options(
            selectinload(Order.items)
        )
    )
    result = db.execute(stmt)
    orders = result.scalars().all()

    assert len(orders) == 2
    assert {order.id for order in orders} == {order_a_id, order_b_id}

    order_by_id = {
        order.id: order
        for order in orders
    }
    assert {
        item.product_name
        for item in order_by_id[order_a_id].items
    } == {"Pen", "Notepad"}
    assert {
        item.product_name
        for item in order_by_id[order_b_id].items
    } == {"Mouse", "Pen"}


def test_joinedload_loading_order_items(db_session) -> None:
    db = db_session

    order_a = Order(title="Order A")
    db.add(order_a)

    order_b = Order(title="Order B")
    db.add(order_b)

    db.commit()

    order_a_item_1 = OrderItem(
        order_id=order_a.id,
        product_name="Pen",
        quantity=1,
        unit_price=1,
    )
    db.add(order_a_item_1)

    order_a_item_2 = OrderItem(
        order_id=order_a.id,
        product_name="Notepad",
        quantity=1,
        unit_price=15,
    )
    db.add(order_a_item_2)

    order_b_item_1 = OrderItem(
        order_id=order_b.id,
        product_name="Mouse",
        quantity=1,
        unit_price=200,
    )
    db.add(order_b_item_1)

    order_b_item_2 = OrderItem(
        order_id=order_b.id,
        product_name="Pen",
        quantity=1,
        unit_price=2,
    )
    db.add(order_b_item_2)
    db.commit()

    order_a_id = order_a.id
    order_b_id = order_b.id

    db.expunge_all()

    stmt = (
        select(Order)
        .options(
            joinedload(Order.items)
        )
    )
    result = db.execute(stmt)
    orders = result.unique().scalars().all()

    assert len(orders) == 2
    assert {order.id for order in orders} == {order_a_id, order_b_id}

    order_by_id = {
        order.id: order
        for order in orders
    }
    assert {
        item.product_name
        for item in order_by_id[order_a_id].items
    } == {"Pen", "Notepad"}
    assert {
        item.product_name
        for item in order_by_id[order_b_id].items
    } == {"Mouse", "Pen"}


def test_sum_quantity_order_items(db_session) -> None:
    db = db_session

    order_a = Order(title="order a")
    db.add(order_a)

    order_b = Order(title="order b")
    db.add(order_b)

    db.commit()

    order_a_item_one = OrderItem(
        order_id=order_a.id,
        product_name="Paper",
        quantity=2,
        unit_price=1,
    )
    db.add(order_a_item_one)

    order_a_item_two = OrderItem(
        order_id=order_a.id,
        product_name="Pen",
        quantity=3,
        unit_price=1,
    )
    db.add(order_a_item_two)

    order_b_item = OrderItem(
        order_id=order_b.id,
        product_name="Soap",
        quantity=4,
        unit_price=2,
    )
    db.add(order_b_item)

    db.commit()

    order_a_id = order_a.id
    order_b_id = order_b.id

    db.expunge_all()

    stmt = (
        select(
            Order.id,
            func.sum(OrderItem.quantity).label("sum_quantity"),
        )
        .join(Order.items)
        .group_by(Order.id)
    )
    rows = db.execute(stmt).all()

    order_ids = [row.id for row in rows]
    assert set(order_ids) == {order_a_id, order_b_id}

    sum_by_order_id = {
        row.id: row.sum_quantity
        for row in rows
    }
    assert sum_by_order_id[order_a_id] == 5
    assert sum_by_order_id[order_b_id] == 4


def test_total_amount_order_items(db_session) -> None:
    db = db_session

    order_a = Order(title="Order A")
    order_b = Order(title="Order B")
    order_c = Order(title="Order C")

    db.add(order_a)
    db.add(order_b)
    db.add(order_c)
    db.commit()

    order_a_item_one = OrderItem(
        order_id=order_a.id,
        product_name="Paper",
        quantity=2,
        unit_price=10,
    )
    order_a_item_two = OrderItem(
        order_id=order_a.id,
        product_name="Pen",
        quantity=3,
        unit_price=15,
    )
    order_b_item = OrderItem(
        order_id=order_b.id,
        product_name="Soap",
        quantity=4,
        unit_price=7,
    )

    db.add(order_a_item_one)
    db.add(order_a_item_two)
    db.add(order_b_item)

    db.commit()

    order_a_id = order_a.id
    order_b_id = order_b.id
    order_c_id = order_c.id

    db.expunge_all()

    stmt = (
        select(
            Order.id,
            func.coalesce(
                func.sum(
                    OrderItem.quantity * OrderItem.unit_price
                ),
                0,
            ).label("total_amount")
        )
        .outerjoin(Order.items)
        .group_by(Order.id)
    )
    rows = db.execute(stmt).all()

    order_ids = [row.id for row in rows]
    assert set(order_ids) == {order_a_id, order_b_id, order_c_id}

    total_by_order_id = {
        row.id: row.total_amount
        for row in rows
    }
    assert total_by_order_id[order_a_id] == Decimal("65.00")
    assert total_by_order_id[order_b_id] == Decimal("28.00")
    assert total_by_order_id[order_c_id] == Decimal("0.00")

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
from app.db.session import SessionLocal
from app.models.order import Order


def test_create_and_read_order():
    test_session_db = SessionLocal()
    try:
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

        test_session_db.delete(order_from_db)
        test_session_db.commit()
    finally:
        test_session_db.close()

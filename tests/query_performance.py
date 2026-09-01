"""tests/query_performance.py"""
from sqlalchemy import text

from app.models.order import Order


def test_performance_experiment(db_session) -> None:
    db = db_session

    target_order = Order(title="Target order")
    background_order = Order(title="Background order")

    db.add(target_order)
    db.add(background_order)

    db.flush()

    target_order_id = target_order.id
    background_order_id = background_order.id

    target_items_stmt = text("""
        INSERT INTO order_items (
                order_id,
                product_name,
                quantity,
                unit_price
        )
        SELECT :target_order_id,
                'Target item ' || gs,
                1,
                10.00
        FROM generate_series(1, 5) as gs
    """)
    db.execute(
        target_items_stmt,
        {"target_order_id": target_order_id},
    )

    background_items_stmt = text("""
        INSERT INTO order_items (
                order_id,
                product_name,
                quantity,
                unit_price
        )
        SELECT :background_order_id,
                'Background item ' || gs,
                1,
                10.00
        FROM generate_series(1, 9995) as gs
    """)
    db.execute(
        background_items_stmt,
        {"background_order_id": background_order_id},
    )

    analyze_stmt = text("""
        ANALYZE order_items
    """)
    db.execute(analyze_stmt)

    order_items_stmt = text("""
        EXPLAIN ANALYZE
        SELECT *
        FROM order_items
        WHERE order_id = :target_order_id
    """)
    rows = db.execute(
        order_items_stmt,
        {"target_order_id": target_order_id}
    ).all()
    print(rows)


    order_items_id_quantity_stmt = text("""
        EXPLAIN ANALYZE
        SELECT order_id, SUM(quantity)
        FROM order_items
        GROUP BY order_id;
    """)
    new_rows = db.execute(order_items_id_quantity_stmt).all()
    print(new_rows)

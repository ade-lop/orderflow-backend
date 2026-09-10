"""tests/concurency.py"""
from threading import Event, Thread

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.models import Order


def test_lost_update_read_committed() -> None:
    assert engine.url.database == "orderflow_test"
    setup_session = SessionLocal()

    order = Order(title="Concurrency order")
    setup_session.add(order)
    setup_session.commit()

    order_id = order.id

    setup_session.close()

    try:
        session_a = SessionLocal()
        session_b = SessionLocal()

        order_a = session_a.get(Order, order_id)
        order_b = session_b.get(Order, order_id)

        assert order_a is not None
        assert order_b is not None

        assert order_a.id == order_b.id
        assert order_a is not order_b

        assert order_a.status == "new"
        assert order_b.status == "new"

        order_a.status = "processing"
        session_a.commit()

        assert order_b.status == "new"

        order_b.status = "canceled"
        session_b.commit()


        cleanup_session = SessionLocal()
        cleanup_order = cleanup_session.get(Order, order_id)
        assert cleanup_order is not None
        assert cleanup_order.status == "canceled"
        cleanup_session.close()

    finally:
        session_a.rollback()
        session_b.rollback()

        session_a.close()
        session_b.close()

        new_cleanup_session = SessionLocal()
        cleanup_order = new_cleanup_session.get(Order, order_id)

        if cleanup_order is not None:
            new_cleanup_session.delete(cleanup_order)
            new_cleanup_session.commit()

        new_cleanup_session.close()


def test_for_update_lock() -> None:
    assert engine.url.database == "orderflow_test"
    #--SETUP SESSION
    b_started = Event()
    b_finished = Event()

    setup_session = SessionLocal()

    order = Order(title="Order for upd lock")
    setup_session.add(order)
    setup_session.commit()

    order_id = order.id
    setup_session.close()

    #--SESSION_A
    session_a = SessionLocal()
    result_a = session_a.execute(select(Order)
                      .where(Order.id == order_id)
                      .with_for_update()
    )
    order_a = result_a.scalar_one()
    assert order_a.status == "new"

    status_seen_by_b: list[str] = []
    #--WORKER_B
    def worker_b() -> None:
        session_b = SessionLocal()
        try:
            b_started.set()
            result_b = session_b.execute(select(Order)
                            .where(Order.id == order_id)
                            .with_for_update()
            )
            order_b = result_b.scalar_one()
            status_seen_by_b.append(order_b.status)
            b_finished.set()
        finally:
            session_b.rollback()
            session_b.close()

    thread_b : Thread | None = None

    try:
        # Далее это уже выполняется в MAIN THREAD
        thread_b = Thread(target=worker_b)
        thread_b.start()
        assert b_started.wait(timeout=1)

        # A пока не отдает lock, B не может получить строку
        assert not b_finished.wait(timeout=0.2)

        # A выполняет действия и отпускает lock
        order_a.status = "processing"
        session_a.commit()

        # после освобождения lock B наконец прошла SELECT FOR UPDATE
        assert b_finished.wait(timeout=1)
        # этот SELECT вернул B обновлённую строку
        assert status_seen_by_b == ["processing"]

        # Main Thread ждёт полного завершения Thread B / worker_b
        thread_b.join(timeout=1)
        assert not thread_b.is_alive()
    finally:
        session_a.rollback()
        # Теперь lock A освобожден
        session_a.close()

        if thread_b is not None:
            # Main Thread ждёт окончания Thread B
            thread_b.join(timeout=1)

        cleanup_session = SessionLocal()
        try:
            order_to_clean = cleanup_session.get(Order, order_id)
            if order_to_clean is not None:
                cleanup_session.delete(order_to_clean)
                cleanup_session.commit()
        finally:
            cleanup_session.close()


def test_repeatable_read_serialization_failure() -> None:
    assert engine.url.database == "orderflow_test"
    setup_session = SessionLocal()
    order = Order(title="Order repeatable read test")
    setup_session.add(order)
    setup_session.commit()

    order_id = order.id
    setup_session.close()

    connection_b = engine.connect()
    connection_b = connection_b.execution_options(
        isolation_level="REPEATABLE READ"
    )
    session_b = Session(bind=connection_b)
    session_a = SessionLocal()
    verify_session = SessionLocal()

    try:
        result = session_b.execute(
            text("SHOW transaction_isolation;")
        )
        assert result.scalar_one() == "repeatable read"

        status_before = session_b.execute(
            select(Order.status)
            .where(Order.id == order_id)
        ).scalar_one()
        assert status_before == "new"

        order_a = session_a.execute(
            select(Order)
            .where(Order.id == order_id)
        ).scalar_one()
        assert order_a.status == "new"

        order_a.status = "processing"
        session_a.commit()

        status_after = session_b.execute(
            select(Order.status)
            .where(Order.id == order_id)
        ).scalar_one()
        assert status_after == "new"

        with pytest.raises(OperationalError) as exc_info:
            session_b.execute(
                text("UPDATE orders SET status = 'canceled' WHERE id = :order_id"),
                {"order_id": order_id}
            )
        assert exc_info.value.orig.sqlstate == "40001"
        session_b.rollback()

        check_status = verify_session.execute(
            select(Order.status)
            .where(Order.id == order_id)
        ).scalar_one()
        assert check_status == "processing"

    finally:
        session_a.rollback()
        session_a.close()

        session_b.rollback()
        session_b.close()
        connection_b.close()

        verify_session.close()

        cleanup_session = SessionLocal()
        try:
            order_to_clean = cleanup_session.get(Order, order_id)
            if order_to_clean is not None:
                cleanup_session.delete(order_to_clean)
                cleanup_session.commit()
        finally:
            cleanup_session.close()

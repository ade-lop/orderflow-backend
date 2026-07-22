import os

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://orderflow:orderflow_password"
    "@localhost:55432/orderflow_test"
)
os.environ["ENVIRONMENT"] = "test"



from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Order


@pytest.fixture
def db_session() -> Generator[tuple[Session, list[int]]]:
    db = SessionLocal()
    created_ids = []

    try:
        yield db, created_ids

    finally:
        try:
            for order_id in created_ids:
                single_order = db.get(Order, order_id)

                if single_order is not None:
                    db.delete(single_order)

            db.commit()
        finally:
            db.close()

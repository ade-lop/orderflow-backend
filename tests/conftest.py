"""
tests/conftest.py
"""
import os

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://orderflow:orderflow_password"
    "@localhost:55432/orderflow_test"
)
os.environ["ENVIRONMENT"] = "test"


import pytest
from sqlalchemy.orm import Session

from app.db.session import engine, get_db
from app.main import app


@pytest.fixture
def db_session():
    connection = engine.connect()
    outer_transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )
    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture
def api_db_override(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield
    finally:
        app.dependency_overrides.pop(get_db, None)

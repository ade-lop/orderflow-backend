"""
test_orders_api.py
"""
from fastapi.testclient import TestClient

from app.main import app
from app.models.order import Order

client = TestClient(app)


def test_create_order(db_session) -> None:
    db, created_ids = db_session

    payload = {
        "title": "test_title"
    }
    response = client.post("/orders", json=payload)

    assert response.status_code == 201

    response_data = response.json()

    created_id = response_data["id"]
    created_ids.append(created_id)

    assert response_data["title"] == "test_title"
    assert created_id is not None
    assert response_data["status"] == "new"
    assert response_data["created_at"] is not None

    test_order = db.get(Order, created_id)
    assert test_order is not None


def test_get_existing_order(db_session) -> None:
    db, created_ids = db_session

    payload = {
        "title": "new_existing_order"
    }
    response = client.post("/orders", json=payload)

    assert response.status_code == 201

    response_data = response.json()

    created_id = response_data["id"]
    created_ids.append(created_id)

    response = client.get(f"/orders/{created_id}")
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["title"] == "new_existing_order"
    assert response_data["id"] == created_id
    assert response_data["status"] == "new"
    assert response_data["created_at"] is not None

    test_order = db.get(Order, created_id)
    assert test_order is not None


def test_get_missing_order() -> None:
    response = client.get("/orders/9999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found"}


def test_list_orders(db_session) -> None:
    _, created_ids = db_session

    payload = {"title": "for_list_order"}

    response = client.post("/orders", json=payload)
    assert response.status_code == 201

    response_data = response.json()
    created_id = response_data["id"]
    created_ids.append(created_id)

    response = client.get("/orders")
    assert response.status_code == 200

    response_data = response.json()
    assert isinstance(response_data, list)

    assert any(
        order["id"] == created_id and order["title"] == "for_list_order"
        for order in response_data
    )

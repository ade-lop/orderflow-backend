"""tests/test_order_items_api.py"""
from fastapi.testclient import TestClient

from app.main import app
from app.models.order import Order
from app.models.order_item import OrderItem

client = TestClient(app)


def test_create_order_item(db_session, api_db_override) -> None:
    db = db_session

    order_payload = {
        "title": "new order",
    }
    response = client.post(
        "/orders",
        json=order_payload,
    )
    assert response.status_code == 201

    response_data = response.json()
    created_order_id = response_data["id"]

    item_payload = {
        "product_name": "product item",
        "quantity": 2,
        "unit_price": 100,
    }
    response = client.post(
        f"/orders/{created_order_id}/items",
        json=item_payload,
    )
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["id"] is not None
    assert response_data["order_id"] == created_order_id
    assert response_data["product_name"] == "product item"
    assert response_data["quantity"] == 2
    assert response_data["unit_price"] == "100.00"

    assert db.get(OrderItem, response_data["id"]) is not None


def test_missing_order_create_order_item(db_session, api_db_override) -> None:
    db = db_session

    assert db.get(Order, 9999) is None

    item_payload = {
        "product_name": "product item",
        "quantity": 2,
        "unit_price": 100,
    }
    response = client.post(
        "/orders/9999/items",
        json=item_payload,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found"}


def test_invalid_quantity_create_order_item(db_session, api_db_override) -> None:
    order_payload = {
        "title": "new order",
    }
    response = client.post(
        "/orders",
        json=order_payload,
    )
    assert response.status_code == 201

    response_data = response.json()
    created_order_id = response_data["id"]

    item_payload = {
        "product_name": "product item",
        "quantity": 0,
        "unit_price": 100,
    }
    response = client.post(
        f"/orders/{created_order_id}/items",
        json=item_payload,
    )
    assert response.status_code == 422


def test_valid_get_order_items(db_session, api_db_override) -> None:
    payload = {"title": "order fro items"}
    response = client.post(
        "/orders",
        json=payload,
    )
    assert response.status_code == 201

    order_id = response.json()["id"]

    payload = {
        "product_name": "item one",
        "quantity": 4,
        "unit_price": 50,
    }
    response = client.post(
        f"/orders/{order_id}/items",
        json=payload,
    )
    assert response.status_code == 201
    item_id_1 = response.json()["id"]

    payload = {
        "product_name": "item two",
        "quantity": 6,
        "unit_price": 25,
    }
    response = client.post(
        f"/orders/{order_id}/items",
        json=payload,
    )
    assert response.status_code == 201
    item_id_2 = response.json()["id"]

    response = client.get(
        f"/orders/{order_id}/items"
    )
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data) == 2

    item_ids = [item["id"] for item in response_data]
    assert set(item_ids) == {item_id_1, item_id_2}


def test_empty_items_get_order_items(db_session, api_db_override) -> None:
    payload = {"title": "order with no items"}
    response = client.post(
        "/orders",
        json=payload,
    )
    assert response.status_code == 201

    order_id = response.json()["id"]

    response = client.get(
        f"/orders/{order_id}/items",
    )
    assert response.status_code == 200
    assert response.json() == []


def test_missing_order_get_order_items(db_session, api_db_override) -> None:
    response = client.get(
        "/orders/99999/items",
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found"}

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


def test_partial_update_order(db_session) -> None:
    db, created_ids = db_session

    payload = {
        "title": "title_to_update",
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 201

    response_data = response.json()
    created_title = response_data["title"]
    created_id = response_data["id"]
    created_ids.append(created_id)

    created_order = db.get(Order, created_id)
    assert created_order is not None

    updated_payload = {
        "status": "canceled",
    }
    response = client.patch(
        f"/orders/{created_id}",
        json=updated_payload,
    )
    assert response.status_code == 200
    db.refresh(created_order)

    assert created_order.title == created_title
    assert created_order.status == "canceled"

    response_updated_data = response.json()

    assert response_updated_data["title"] == created_title
    assert response_updated_data["status"] == "canceled"


def test_update_all_allowed_order_fields(db_session) -> None:
    db, created_ids = db_session

    payload = {
        "title": "for_full_upd_title"
    }

    response = client.post(
        "/orders",
        json=payload
    )
    assert response.status_code == 201

    response_data = response.json()
    created_id = response_data["id"]

    created_ids.append(created_id)
    created_order = db.get(Order, created_id)
    assert created_order is not None

    updated_payload = {
        "title": "updated_title",
        "status": "processing",
    }

    response = client.patch(
        f"/orders/{created_id}",
        json=updated_payload,
    )
    assert response.status_code == 200

    db.refresh(created_order)

    response_updated_data = response.json()

    assert response_updated_data["id"] == created_id
    assert response_updated_data["title"] == "updated_title"
    assert response_updated_data["status"] == "processing"

    assert created_order.title == "updated_title"
    assert created_order.status == "processing"


def test_invalid_update_order(db_session) -> None:
    db, created_ids = db_session

    payload = {
        "title": "next order",
    }
    response = client.post(
        "/orders",
        json=payload,
    )
    assert response.status_code == 201

    response_data = response.json()
    created_title = response_data["title"]
    created_status = response_data["status"]
    created_id = response_data["id"]
    created_ids.append(created_id)

    created_order = db.get(Order, created_id)
    assert created_order is not None

    update_payload = {
        "status": "unknown",
    }
    response = client.patch(
        f"/orders/{created_id}",
        json=update_payload,
    )
    assert response.status_code == 422

    db.refresh(created_order)
    assert created_order.title == created_title
    assert created_order.status == created_status


def test_update_missing_order() -> None:
    valid_payload = {
        "status": "completed",
    }
    response = client.patch(
        "/orders/99999",
        json=valid_payload,
    )
    assert response.status_code == 404

    response_data = response.json()
    assert response_data == {"detail": "Order not found"}


def test_empty_update_order(db_session) -> None:
    db, created_ids = db_session

    payload = {
        "title": "new order",
    }
    response = client.post(
        "/orders",
        json=payload,
    )
    assert response.status_code == 201

    response_data = response.json()
    created_id = response_data["id"]
    created_ids.append(created_id)
    created_title = response_data["title"]
    created_status = response_data["status"]

    created_order = db.get(Order, created_id)
    assert created_order is not None

    empty_payload = {}
    response = client.patch(
        f"/orders/{created_id}",
        json=empty_payload,
    )
    assert response.status_code == 200

    response_data = response.json()

    assert response_data["title"] == created_title
    assert response_data["status"] == created_status

    db.refresh(created_order)

    assert created_order.title == created_title
    assert created_order.status == created_status


def test_delete_order(db_session) -> None:
    db, created_ids = db_session

    payload = {
        "title": "Order to delete",
    }
    response = client.post(
        "/orders",
        json=payload,
    )
    assert response.status_code == 201

    response_data = response.json()
    created_id = response_data["id"]
    created_ids.append(created_id)

    created_order = db.get(Order, created_id)
    assert created_order is not None

    response = client.delete(
        f"/orders/{created_id}",
    )
    assert response.status_code == 204
    assert response.content == b""

    db.expire_all()

    deleted_order = db.get(Order, created_id)
    assert deleted_order is None

    response = client.get(f"/orders/{created_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found"}


def test_delete_missing_order() -> None:
    response = client.delete("/orders/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found"}

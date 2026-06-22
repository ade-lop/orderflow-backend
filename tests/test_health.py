from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_app_uses_settings_tittle() -> None:
    assert app.title == "Orderflow-backend"

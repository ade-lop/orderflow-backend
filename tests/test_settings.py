import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_use_defaults(monkeypatch) -> None:
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)

    setting_object = Settings(
        database_url="postgresql+psycopg://user:password@localhost:55432/orderflow",
        _env_file=None,
    )
    assert setting_object.app_name == "Orderflow-backend"
    assert setting_object.environment == "local"
    assert setting_object.debug is False
    assert (
        setting_object.database_url
          == "postgresql+psycopg://user:password@localhost:55432/orderflow"
    )

def test_settings_read_environment_vars(monkeypatch) -> None:
    monkeypatch.setenv("APP_NAME", "Test App")

    settings = Settings(
        database_url="postgresql+psycopg://user:password@localhost:55432/orderflow",
        _env_file=None,
    )

    assert settings.app_name == "Test App"

def test_settings_required_database_url(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)

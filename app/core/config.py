from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Orderflow-backend"
    environment: Literal["local", "test", "production"] = "local"
    debug: bool = False
    database_url: str

    # Загрузка .env согласно доке
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings() -> Settings:
    return Settings()

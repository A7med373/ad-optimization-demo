from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ad Optimization Demo"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ad_optimization"
    telegram_bot_token: str = "demo-telegram-bot-token"
    telegram_admin_chat_id: int = 123456789
    attribution_window_hours: int = 72
    match_threshold: float = 0.60
    yandex_metrika_counter_id: str = "demo-counter"
    yandex_metrika_token: str = "demo-token"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()

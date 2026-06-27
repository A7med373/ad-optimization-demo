from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ad Optimization Demo"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ad_optimization"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:29092"
    kafka_topic_clicks: str = "ad.clicks"
    kafka_topic_orders: str = "marketplace.orders"
    attribution_window_hours: int = 72
    match_threshold: float = 0.60
    yandex_metrika_counter_id: str = "demo-counter"
    yandex_metrika_token: str = "demo-token"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


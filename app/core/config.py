from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FiscalBot"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://fiscalbot:fiscalbot@localhost:5432/fiscalbot"
    api_v1_prefix: str = "/api/v1"
    frontend_url: str = "http://localhost:5173"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    redis_url: str = "redis://localhost:6379/0"
    storage_path: str = "storage"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from: str = "noreply@fiscalbot.local"
    admin_email: str = "admin@fiscalbot.gov.br"
    admin_password: str = "fiscalbot123"
    celery_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

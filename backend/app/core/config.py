"""Configuration module centralising environment driven settings."""

from functools import lru_cache
from typing import Sequence

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "Tax Lien Strategist"
    VERSION: str = "0.1.0"

    API_V1_PREFIX: str = "/api"
    CORS_ALLOW_ORIGINS: list[AnyHttpUrl | str] = ["*"]

    DATABASE_URL: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600

    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL_NAME: str = "gpt-5.1"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    HUGGINGFACE_API_KEY: str | None = None
    HUGGINGFACE_EMBEDDING_MODEL: str | None = None

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    REASONING_LOG_RETENTION_DAYS: int = 30
    AGENT_MAX_TOOL_RETRIES: int = 3

    ANALYSIS_DEFAULT_MAX_BUDGET: int = 500_000
    ANALYSIS_DEFAULT_PAGE_SIZE: int = 100

    @field_validator("CORS_ALLOW_ORIGINS", mode="before")
    @classmethod
    def split_cors(cls, value: str | Sequence[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return list(value)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

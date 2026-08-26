from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "AI-200 KnowledgeHub Search API"
    app_version: str = "0.2.0"
    environment: str = "local"
    log_level: str = "INFO"

    database_url: str = (
        "postgresql+psycopg://"
        "knowledgehub:knowledgehub@localhost:5432/knowledgehub"
    )

    sql_echo: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
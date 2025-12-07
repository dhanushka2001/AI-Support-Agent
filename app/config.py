from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    ENVIRONMENT: str
    CORS_ALLOWED_ORIGINS: List[str]

    # Later you can add:
    # OPENAI_API_KEY: str
    # DB_URL: str

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8"
    )


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

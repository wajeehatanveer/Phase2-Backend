from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    database_url: str
    better_auth_secret: str
    better_auth_url: str

    model_config = SettingsConfigDict(env_file=str(Path(__file__).parent / ".env"))


settings = Settings()
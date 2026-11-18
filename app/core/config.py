"""Validated application settings; no external services are initialized here."""

from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = Field(default="AI Task & Document Assistant", min_length=1)
    app_env: Literal["development", "test", "production"] = "development"
    debug: bool = False
    api_host: str = Field(default="127.0.0.1", min_length=1)
    api_port: int = Field(default=8000, ge=1, le=65535)
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    llm_api_key: SecretStr = SecretStr("")
    llm_base_url: str = ""
    llm_model: str = ""
    database_url: str = "sqlite:///./data/app.db"
    log_level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"] = (
        "INFO"
    )

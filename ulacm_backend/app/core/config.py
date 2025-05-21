# File: ulacm_backend/app/core/config.py
# Purpose: Application configuration using Pydantic BaseSettings.
# Loads settings primarily from environment variables and .env file.
# Defaults in this file are only used if not overridden by env/.env.
# Added OLLAMA_MODEL and OLLAMA_TEMPERATURE settings.
# Added ADMIN_SYSTEM_TEAM_ID.
# Updated BACKEND_CORS_ORIGINS to handle potential HTTPS URLs.

import secrets
from typing import List, Union, Optional
from uuid import UUID # Import UUID for ADMIN_SYSTEM_TEAM_ID

from pydantic import AnyHttpUrl, PostgresDsn, field_validator, HttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    Environment variables take precedence over .env file values.
    Defaults defined here are used only if the setting is not found elsewhere.
    """
    PROJECT_NAME: str = "ULACM Service (Dev)"
    PROJECT_VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"

    SESSION_SECRET_KEY: str = secrets.token_hex(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8
    ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 1
    ADMIN_PASSWORD: str
    ADMIN_USERNAME: str = "admin" # Default admin username for token subject

    # Fixed UUID for the "Admin System Team"
    # This ID will be used to own Templates and Workflows created by Admins.
    # It must match the one inserted in init_db.sql.
    ADMIN_SYSTEM_TEAM_ID: UUID = UUID("04a9a4ec-18d8-4cfd-bead-d0ef99199e17")
    # Must match frontend ADMIN_SYSTEM_TEAM_ID_STRING in ulacm_frontend/src/utils/constants.ts

    # Ensure BACKEND_CORS_ORIGINS can handle https URLs
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and v and not v.startswith("["):
            # Ensure that passed origins can be parsed as AnyHttpUrl (which includes https)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, (list, str)):
            return v
        return []

    DATABASE_URL: PostgresDsn
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    # --- Ollama ---
    OLLAMA_API_URL: HttpUrl = Field(default_factory=lambda: HttpUrl("http://host.docker.internal:11434"))
    OLLAMA_MODEL: str = "ollama/llama3:latest"
    OLLAMA_TEMPERATURE: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

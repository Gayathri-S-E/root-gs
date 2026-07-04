"""
Core Configuration — Pydantic Settings
All environment variables are loaded here.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Any


class Settings(BaseSettings):
    # ─── Application ──────────────────────────────────────────────
    APP_NAME: str = "ROOTGS"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-secret-key-in-production-minimum-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ─── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://rootgs:rootgs_secret@localhost:5432/rootgs_db"

    # ─── Redis ────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"

    # ─── AI APIs ──────────────────────────────────────────────────
    GOOGLE_GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    # ─── Weather ──────────────────────────────────────────────────
    OPENWEATHER_API_KEY: str = ""
    # Open-Meteo is free — used as primary weather provider

    # ─── Storage ──────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = "rootgs-media"
    AWS_REGION: str = "ap-south-1"
    AWS_S3_ENDPOINT_URL: str = "https://s3.amazonaws.com"

    # ─── CORS ─────────────────────────────────────────────────────
    ALLOWED_ORIGINS: Any = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ─── Email ────────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM: str = "noreply@rootgs.ai"

    # ─── Feature Flags ────────────────────────────────────────────
    ENABLE_AI_FEATURES: bool = True
    ENABLE_VOICE_SUPPORT: bool = True
    AI_DEMO_MODE: bool = True  # Returns mock AI when no API key

    # ─── Pagination ───────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ─── AI Cache TTL ─────────────────────────────────────────────
    WEATHER_CACHE_TTL: int = 1800     # 30 minutes
    MARKET_CACHE_TTL: int = 1800      # 30 minutes
    AI_RESPONSE_CACHE_TTL: int = 300  # 5 minutes

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()

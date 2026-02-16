"""
Application configuration using Pydantic Settings.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    APP_NAME: str = "BuffetGPT"
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]

    # Vision
    VISION_MODEL: str = "yolov8"  # yolov8 | gemini
    GEMINI_API_KEY: Optional[str] = None

    # Stomach physics
    STOMACH_CAPACITY_LITERS: float = 1.35
    STOMACH_CAPACITY_ML: float = 1350

    # Optimization
    DEFAULT_CALORIE_LIMIT: int = 2000
    DEFAULT_GOAL: str = "enjoyment_first"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()

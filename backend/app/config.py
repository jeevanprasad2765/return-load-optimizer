from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Empty Return Load Optimizer"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./optimizer.db"
    
    # Auth
    JWT_SECRET: str = "supersecretkey_empty_return_load_optimizer_2026_dev"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # OSRM Router
    OSRM_BASE_URL: str = "https://router.project-osrm.org"
    
    # Map Provider
    MAPBOX_ACCESS_TOKEN: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

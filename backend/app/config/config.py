import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "FitnessPR API"
    version: str = "0.1.0"
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Database
    database_url: str = Field(
        default="sqlite:///./fitness_pr.db",
        description="Database connection URL"
    )
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-this-in-production",
        description="Secret key for JWT encoding"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiration in days"
    )
    
    # CORS
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    
    # File uploads
    upload_dir: str = Field(default="uploads", description="Upload directory")
    max_file_size: int = Field(
        default=10 * 1024 * 1024, description="Maximum file size in bytes (10MB)"
    )
    
    # Pagination
    default_page_size: int = Field(default=20, description="Default page size")
    max_page_size: int = Field(default=100, description="Maximum page size")
    
    # Environment
    environment: str = Field(default="development", description="Environment name")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_to_file: bool = Field(default=True, description="Enable file logging")
    log_rotation_size: str = Field(default="10MB", description="Log rotation size")
    log_retention_days: int = Field(default=30, description="Log retention in days")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()

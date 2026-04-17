"""Application configuration"""
from decimal import Decimal
from typing import Dict, List, Any, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Known insecure / leaked placeholder values that must never be used in
# production. Configuration validation will reject these.
INSECURE_SECRET_KEY_VALUES = {
    "your-secret-key-change-in-production",
    "thfhhvjHHTTDHHDJJHDRKHLIULRNJLGXVLBH",
    "dev-secret-key-for-development-only-change-in-production-min-32-chars",
}


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "RH Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database: must be provided via environment variable in production.
    # No default credentials are hardcoded to avoid leaking production secrets
    # through source control.
    DATABASE_URL: str = ""

    # Security
    # SECRET_KEY MUST be provided via environment variable in production.
    # The placeholder below is intentionally non-secret and is rejected by
    # validate_configuration() when DEBUG=False.
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://hr-m-syst.vercel.app",

    ]

    # Permissions
    AUTO_CREATE_PERMISSIONS: bool = True

    # Security System
    # Enable/disable authentication (JWT token validation)
    # Set to False for testing/development without authentication
    AUTHENTICATION_ENABLED: bool = True

    # Enable/disable permission checks.
    # Enabled by default — it is safer to fail closed and explicitly opt out
    # for development via environment variable than the other way round.
    PERMISSION_CHECK_ENABLED: bool = True

    # Leave Management Configuration
    CONGE__DEFAULT_COUNTRY_CODE: str = "BI"
    CONGE__HOLIDAYS_AUTO_LOAD: bool = True
    CONGE__MAX_VALIDATION_LEVELS: int = 5
    CONGE__MAX_DOCUMENT_SIZE_MB: int = 100
    CONGE__ALLOWED_DOCUMENT_TYPES: str = "pdf,jpg,jpeg,png"

    # SUPABASE — must be provided via environment variables. No default keys
    # are hardcoded.
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_BUCKET_NAME: str = "uploads"
    # Storage backend: "local" (filesystem) or "supabase"
    STORAGE_BACKEND: str = "local"

    # Email/SMTP Configuration — must be provided via environment variables.
    # No default credentials are hardcoded.
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_TLS: bool = True
    NOTIFICATIONS_ENABLED: bool = False

    # Audit System
    AUDIT_ENABLED: bool = True  # Enable/disable audit logging
    AUDIT_RETENTION_DAYS: int = 90  # Days to keep audit logs
    AUDIT_SKIP_PATHS: list[str] = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
        "/health",
        "/metrics",
        "/static"
    ]  # Paths to skip from audit logging
    AUDIT_SENSITIVE_FIELDS: list[str] = [
        "password",
        "passwd",
        "pwd",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "secret_key",
        "api_key",
        "authorization",
        "csrf_token",
        "credit_card",
        "card_number",
        "cvv",
        "ssn",
        "social_security",
        "private_key",
        "encryption_key"
    ]  # Sensitive fields to mask in audit logs

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


# Global settings instances
settings = Settings()

def validate_configuration() -> None:
    """
    Validate configuration at startup.
    Raises ValueError if configuration is invalid.
    """
    try:
        secret_key = settings.SECRET_KEY

        # In production (DEBUG=False), enforce strict SECRET_KEY validation
        if not settings.DEBUG:
            if not secret_key or secret_key in INSECURE_SECRET_KEY_VALUES:
                raise ValueError(
                    "SECRET_KEY must be set to a secure value in production "
                    "(detected an insecure placeholder or empty value)"
                )

            if len(secret_key) < 32:
                raise ValueError(
                    "SECRET_KEY must be at least 32 characters long"
                )

            if not settings.DATABASE_URL:
                raise ValueError(
                    "DATABASE_URL must be set via environment variable in "
                    "production"
                )
        else:
            # In development (DEBUG=True), just warn if using default key
            if secret_key in INSECURE_SECRET_KEY_VALUES:
                print("⚠️  Warning: Using default SECRET_KEY (OK for development only)")

        print("✓ Configuration validation successful")

    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        raise ValueError(f"Configuration validation failed: {e}") from e

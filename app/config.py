from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # --- App Info ---
    APP_NAME: str = "FastAPI Product Management API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # --- Auth ---
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    # Token expiry: 240 minutes = 4 hours
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 240

    # --- PostgreSQL ---
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str

    # --- MongoDB ---
    MONGODB_URL: str = ""
    MONGODB_DB_NAME: str = ""

    # --- Supabase ---
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["*"]

    # --- Pydantic Settings config ---
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"
    }

    # --- Computed properties ---
    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def async_postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


# Singleton instance
settings = Settings()

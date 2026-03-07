from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    EXTRA_CORS_ORIGINS: str = ""

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    @property
    def cors_origins(self) -> list[str]:
        origins = [self.FRONTEND_URL]
        if self.EXTRA_CORS_ORIGINS:
            origins.extend(
                o.strip() for o in self.EXTRA_CORS_ORIGINS.split(",") if o.strip()
            )
        return origins

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

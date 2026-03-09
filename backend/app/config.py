from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "ridgerest"
    MONGODB_TLS_ALLOW_INVALID_CERTIFICATES: bool = False

    # Clerk Auth
    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    EXTRA_CORS_ORIGINS: str = ""

    # Feature flags
    ENABLE_DDTRACE: bool = False

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

import logging as _logging
_log = _logging.getLogger(__name__)
if not settings.CLERK_SECRET_KEY or not settings.CLERK_PUBLISHABLE_KEY:
    _log.critical(
        "CLERK_SECRET_KEY and/or CLERK_PUBLISHABLE_KEY are not set. "
        "Authentication will be disabled. Set these env vars in Render."
    )

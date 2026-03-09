from fastapi.middleware.cors import CORSMiddleware
from app.config import settings


def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
        max_age=600,
    )

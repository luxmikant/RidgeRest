import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# ddtrace auto-instrumentation (enabled via ENABLE_DDTRACE=true)
if os.getenv("ENABLE_DDTRACE", "false").lower() == "true":
    try:
        from ddtrace import patch_all

        patch_all()
    except ImportError:
        pass

import socketio
from fastapi import FastAPI

from app.config import settings
from app.core.cors import add_cors_middleware
from app.database import create_indexes
from app.routers import analytics, auth, balance, leaves
from app.socket_manager import sio

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ridgerest")

# Create FastAPI app
fastapi_app = FastAPI(
    title="RidgeRest API",
    description="Leave Management System API",
    version="1.0.0",
)

# CORS
add_cors_middleware(fastapi_app)

# Include routers
fastapi_app.include_router(auth.router)
fastapi_app.include_router(leaves.router)
fastapi_app.include_router(balance.router)
fastapi_app.include_router(analytics.router)

# Mount Socket.IO
sio.cors_allowed_origins = settings.cors_origins
socket_app = socketio.ASGIApp(sio, fastapi_app, socketio_path="/ws/socket.io")


@fastapi_app.on_event("startup")
async def startup():
    logger.info("Starting RidgeRest API...")
    try:
        from app.database import ping_database

        await ping_database()
        logger.info("MongoDB connection verified")
        await create_indexes()
        logger.info("Database indexes created")
        fastapi_app.state.database_ready = True
    except Exception as exc:
        fastapi_app.state.database_ready = False
        logger.error("Database startup failed: %s", exc, exc_info=True)


@fastapi_app.get("/api/health")
async def health():
    database_ok = getattr(fastapi_app.state, "database_ready", False)

    return {
        "status": "ok" if database_ok else "degraded",
        "service": "ridgerest-backend",
        "database": "up" if database_ok else "down",
    }


# Use socket_app as the ASGI entry point (wraps FastAPI + Socket.IO)
app = socket_app

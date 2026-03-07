import logging
import sys

from dotenv import load_dotenv

load_dotenv()

# ddtrace auto-instrumentation (must be before FastAPI import in production)
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
app = FastAPI(
    title="RidgeRest API",
    description="Leave Management System API",
    version="1.0.0",
)

# CORS
add_cors_middleware(app)

# Include routers
app.include_router(auth.router)
app.include_router(leaves.router)
app.include_router(balance.router)
app.include_router(analytics.router)

# Mount Socket.IO
sio.cors_allowed_origins = settings.cors_origins
socket_app = socketio.ASGIApp(sio, app, socketio_path="/ws/socket.io")


@app.on_event("startup")
async def startup():
    logger.info("Starting RidgeRest API...")
    await create_indexes()
    logger.info("Database indexes created")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "ridgerest-backend"}


# Use socket_app as the ASGI entry point (wraps FastAPI + Socket.IO)
app = socket_app

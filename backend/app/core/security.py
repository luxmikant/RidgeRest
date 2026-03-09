import base64
import logging
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt import PyJWKClient

from app.config import settings
from app.database import users_collection

logger = logging.getLogger(__name__)


def _clerk_jwks_url() -> str:
    """Derive JWKS URL from Clerk publishable key (pk_live_<base64(domain)>)."""
    if not settings.CLERK_PUBLISHABLE_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth not configured: CLERK_PUBLISHABLE_KEY missing from environment.",
        )
    pk = settings.CLERK_PUBLISHABLE_KEY
    parts = pk.split("_", 2)
    encoded = parts[2] if len(parts) == 3 else pk
    # Pad to multiple of 4
    pad = 4 - len(encoded) % 4
    if pad != 4:
        encoded += "=" * pad
    domain = base64.b64decode(encoded).decode().rstrip("$")
    return f"https://{domain}/.well-known/jwks.json"


@lru_cache(maxsize=1)
def _jwks_client() -> PyJWKClient:
    url = _clerk_jwks_url()
    logger.info("Clerk JWKS URL: %s", url)
    return PyJWKClient(url, cache_jwk_set=True, lifespan=300)


def _verify_clerk_token(token: str) -> dict:
    try:
        client = _jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except Exception as exc:
        logger.warning("Token verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


async def get_clerk_user_id(request: Request) -> str:
    """Verify Clerk JWT and return the Clerk user ID — no DB lookup."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = auth_header[7:]
    payload = _verify_clerk_token(token)
    clerk_user_id = payload.get("sub")
    if not clerk_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )
    return clerk_user_id


async def get_current_user(request: Request) -> dict:
    """Verify Clerk JWT and load the MongoDB user profile."""
    clerk_user_id = await get_clerk_user_id(request)
    user = await users_collection.find_one({"clerk_id": clerk_user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User profile not found. Please complete account setup.",
        )
    user["id"] = user["clerk_id"]
    return user


async def require_employee(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee access required",
        )
    return user


async def require_employer(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employer access required",
        )
    return user


async def require_employee(user: dict = Depends(get_current_user)):
    if user.get("role") != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee access required",
        )
    return user


async def require_employer(user: dict = Depends(get_current_user)):
    if user.get("role") != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employer access required",
        )
    return user

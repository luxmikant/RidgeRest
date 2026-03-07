import base64
import json
import secrets
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException, status

from app.config import settings
from app.database import oauth_states_collection

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


async def create_google_auth_url(role: str) -> str:
    """Build Google OAuth authorization URL with CSRF-safe state."""
    nonce = secrets.token_urlsafe(32)

    # Store nonce + role in DB (TTL 10 min)
    await oauth_states_collection.insert_one(
        {
            "nonce": nonce,
            "role": role,
            "created_at": datetime.now(timezone.utc),
        }
    )

    state = base64.urlsafe_b64encode(json.dumps({"nonce": nonce}).encode()).decode()

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }

    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


async def verify_state_and_get_role(state: str) -> str:
    """Verify the OAuth state nonce and return the associated role."""
    try:
        decoded = json.loads(base64.urlsafe_b64decode(state))
        nonce = decoded.get("nonce")
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth state",
        )

    if not nonce:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing nonce in state",
        )

    # Find and delete the nonce (one-time use)
    state_doc = await oauth_states_collection.find_one_and_delete({"nonce": nonce})
    if not state_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state",
        )

    return state_doc["role"]


async def exchange_code_for_userinfo(code: str) -> dict:
    """Exchange authorization code for Google user info."""
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for tokens",
            )

        tokens = token_response.json()
        access_token = tokens.get("access_token")

        # Fetch user info
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch Google user info",
            )

        return userinfo_response.json()

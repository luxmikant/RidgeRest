import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.core.security import get_clerk_user_id, get_current_user
from app.database import leave_balances_collection, users_collection
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_response(user: dict) -> UserResponse:
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        role=user["role"],
        department=user.get("department", ""),
        auth_provider=user.get("auth_provider", "clerk"),
        created_at=user.get("created_at", datetime.now(timezone.utc)),
    )


async def _init_leave_balance(clerk_user_id: str):
    year = datetime.now(timezone.utc).year
    existing = await leave_balances_collection.find_one(
        {"employee_id": clerk_user_id, "year": year}
    )
    if not existing:
        await leave_balances_collection.insert_one(
            {
                "employee_id": clerk_user_id,
                "year": year,
                "sick": {"total": 10, "used": 0},
                "casual": {"total": 10, "used": 0},
                "annual": {"total": 15, "used": 0},
            }
        )


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return _user_response(user)


@router.patch("/me/role")
async def set_role(body: dict, clerk_user_id: str = Depends(get_clerk_user_id)):
    """
    Called after Clerk signup to create the MongoDB profile and assign a role.
    Body: { "role": "employee"|"employer", "name": "...", "email": "..." }
    """
    role = body.get("role")
    if role not in ("employee", "employer"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="role must be 'employee' or 'employer'",
        )

    name = body.get("name", "")
    email = body.get("email", "")
    department = body.get("department", "")

    existing = await users_collection.find_one({"clerk_id": clerk_user_id})
    if not existing:
        user_doc = {
            "clerk_id": clerk_user_id,
            "name": name,
            "email": email,
            "role": role,
            "department": department,
            "auth_provider": "clerk",
            "created_at": datetime.now(timezone.utc),
        }
        await users_collection.insert_one(user_doc)
        if role == "employee":
            await _init_leave_balance(clerk_user_id)
        logger.info("New user profile created: %s role=%s", email, role)
    else:
        await users_collection.update_one(
            {"clerk_id": clerk_user_id},
            {
                "$set": {
                    "role": role,
                    "name": name or existing.get("name", ""),
                    "email": email or existing.get("email", ""),
                }
            },
        )
        logger.info("User role updated: %s -> %s", existing.get("email"), role)

    # Sync role to Clerk publicMetadata so the frontend can read it
    if settings.CLERK_SECRET_KEY:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.patch(
                    f"https://api.clerk.com/v1/users/{clerk_user_id}",
                    headers={
                        "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={"public_metadata": {"role": role}},
                    timeout=10,
                )
                resp.raise_for_status()
        except Exception as exc:
            logger.warning("Failed to sync role to Clerk metadata: %s", exc)

    return {"message": "Role set successfully", "role": role}

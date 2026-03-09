import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.core.security import get_clerk_user_id, get_current_user
from app.database import leave_balances_collection, users_collection
from app.schemas.user import RoleEnum, UserResponse

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
        # Non-fatal — MongoDB is source of truth for the backend

    return {"message": "Role set successfully", "role": role}



def _user_response(user: dict) -> UserResponse:
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        role=user["role"],
        department=user.get("department", ""),
        auth_provider=user.get("auth_provider", "local"),
        created_at=user.get("created_at", datetime.now(timezone.utc)),
    )


def _set_token_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=not settings.FRONTEND_URL.startswith("http://localhost"),
        max_age=settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        path="/",
    )


async def _init_leave_balance(employee_id: str):
    year = datetime.now(timezone.utc).year
    existing = await leave_balances_collection.find_one(
        {"employee_id": employee_id, "year": year}
    )
    if not existing:
        await leave_balances_collection.insert_one(
            {
                "employee_id": employee_id,
                "year": year,
                "sick": {"total": 10, "used": 0},
                "casual": {"total": 10, "used": 0},
                "annual": {"total": 15, "used": 0},
            }
        )


@router.post("/signup", response_model=TokenResponse)
async def signup(data: UserSignup, response: Response):
    existing = await users_collection.find_one({"email": data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user_doc = {
        "name": data.name,
        "email": data.email,
        "hashed_password": hash_password(data.password),
        "role": data.role.value,
        "department": data.department,
        "auth_provider": "local",
        "google_id": None,
        "created_at": datetime.now(timezone.utc),
    }

    result = await users_collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    # Init leave balance for employees
    if data.role == RoleEnum.employee:
        await _init_leave_balance(str(result.inserted_id))

    token = create_access_token(
        {"sub": str(result.inserted_id), "email": data.email, "role": data.role.value}
    )
    _set_token_cookie(response, token)

    logger.info("User signed up: %s role=%s", data.email, data.role.value)
    return TokenResponse(message="Signup successful", user=_user_response(user_doc))


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, response: Response):
    user = await users_collection.find_one({"email": data.email})
    if not user or not user.get("hashed_password"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(data.password, user["hashed_password"]):
        logger.warning("Failed login attempt for: %s", data.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(
        {"sub": str(user["_id"]), "email": user["email"], "role": user["role"]}
    )
    _set_token_cookie(response, token)

    logger.info("User logged in: %s", data.email)
    return TokenResponse(message="Login successful", user=_user_response(user))


@router.get("/google")
async def google_login(role: RoleEnum):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured",
        )
    url = await create_google_auth_url(role.value)
    return RedirectResponse(url=url)


@router.get("/google/callback")
async def google_callback(code: str, state: str, response: Response):
    role = await verify_state_and_get_role(state)
    userinfo = await exchange_code_for_userinfo(code)

    google_id = userinfo.get("id")
    email = userinfo.get("email")
    name = userinfo.get("name", email.split("@")[0] if email else "User")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account has no email",
        )

    # Upsert: find by google_id or email
    user = await users_collection.find_one(
        {"$or": [{"google_id": google_id}, {"email": email}]}
    )

    if user:
        # Update google_id if missing
        if not user.get("google_id"):
            await users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"google_id": google_id, "auth_provider": "google"}},
            )
            user["google_id"] = google_id
            user["auth_provider"] = "google"
    else:
        # Create new user
        user_doc = {
            "name": name,
            "email": email,
            "hashed_password": None,
            "role": role,
            "department": "",
            "auth_provider": "google",
            "google_id": google_id,
            "created_at": datetime.now(timezone.utc),
        }
        result = await users_collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        user = user_doc

        if role == "employee":
            await _init_leave_balance(str(result.inserted_id))

    token = create_access_token(
        {"sub": str(user["_id"]), "email": user["email"], "role": user["role"]}
    )

    redirect_url = f"{settings.FRONTEND_URL}/oauth-callback"
    resp = RedirectResponse(url=redirect_url)
    resp.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=not settings.FRONTEND_URL.startswith("http://localhost"),
        max_age=settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        path="/",
    )

    logger.info("Google OAuth login: %s role=%s", email, user["role"])
    return resp


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return _user_response(user)


@router.post("/logout")
async def logout(request=None, response: Response = None, user: dict = Depends(get_current_user)):
    token = request.cookies.get("access_token") if request else None
    if token:
        payload = decode_token(token)
        jti = payload.get("jti")
        if jti:
            await revoked_tokens_collection.insert_one(
                {"jti": jti, "revoked_at": datetime.now(timezone.utc)}
            )

    if response:
        response.delete_cookie("access_token", path="/")

    logger.info("User logged out: %s", user.get("email"))
    return {"message": "Logged out successfully"}

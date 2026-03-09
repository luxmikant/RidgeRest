"""
Migrate existing MongoDB users to Clerk.

Usage:
    cd backend
    python -m scripts.migrate_users_to_clerk

What it does:
    1. Reads all users from MongoDB that don't already have a clerk_id
    2. Creates each user in Clerk via the Clerk Backend API
    3. Sets their role in Clerk publicMetadata
    4. Updates the MongoDB doc with the returned clerk_id
    5. Updates all leaves + leave_balances to use the new clerk_id as employee_id

After migration, existing users can log in via Clerk "Forgot password?" to set a password.
Google-auth users can sign in with Google (Clerk matches by email).
"""
import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "")
if not CLERK_SECRET_KEY:
    raise SystemExit("CLERK_SECRET_KEY is not set in .env")


async def main():
    # Import here so dotenv has already been loaded
    from app.database import leave_balances_collection, leaves_collection, users_collection

    users = await users_collection.find({"clerk_id": {"$exists": False}}).to_list(length=10000)
    print(f"Found {len(users)} users to migrate")

    async with httpx.AsyncClient(timeout=15) as client:
        for user in users:
            email = user.get("email", "")
            role = user.get("role", "employee")
            name = user.get("name", "")
            old_id = str(user["_id"])

            # Split name into first/last
            parts = name.split(" ", 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""

            resp = await client.post(
                "https://api.clerk.com/v1/users",
                headers={
                    "Authorization": f"Bearer {CLERK_SECRET_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "email_address": [email],
                    "first_name": first_name or None,
                    "last_name": last_name or None,
                    "skip_password_checks": True,
                    "skip_password_requirement": True,
                    "public_metadata": {"role": role},
                },
            )

            if resp.status_code in (200, 201):
                clerk_user = resp.json()
                clerk_id = clerk_user["id"]

                # Update MongoDB user with clerk_id
                await users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"clerk_id": clerk_id}},
                )

                # Update leaves: replace old ObjectId string with clerk_id
                r1 = await leaves_collection.update_many(
                    {"employee_id": old_id},
                    {"$set": {"employee_id": clerk_id}},
                )

                # Update leave_balances the same way
                r2 = await leave_balances_collection.update_many(
                    {"employee_id": old_id},
                    {"$set": {"employee_id": clerk_id}},
                )

                print(
                    f"✓ {email} → {clerk_id}  "
                    f"(leaves: {r1.modified_count}, balances: {r2.modified_count})"
                )

            elif resp.status_code == 422:
                # User already exists in Clerk — fetch by email to get clerk_id
                search_resp = await client.get(
                    "https://api.clerk.com/v1/users",
                    headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"},
                    params={"email_address": email},
                )
                if search_resp.status_code == 200 and search_resp.json():
                    clerk_id = search_resp.json()[0]["id"]
                    await users_collection.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"clerk_id": clerk_id}},
                    )
                    print(f"~ {email} already in Clerk → {clerk_id}")
                else:
                    print(f"✗ {email}: 422 and not found by email search")
            else:
                print(f"✗ {email}: HTTP {resp.status_code} — {resp.text[:200]}")

    print("\nMigration complete.")


asyncio.run(main())

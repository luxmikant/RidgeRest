import certifi
import motor.motor_asyncio
from app.config import settings

_mongo_opts: dict = {
    "tls": True,
    "tlsCAFile": certifi.where(),
    "serverSelectionTimeoutMS": 10000,
}
if settings.MONGODB_TLS_ALLOW_INVALID_CERTIFICATES:
    _mongo_opts["tlsAllowInvalidCertificates"] = True

client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.MONGODB_URL, **_mongo_opts
)
db = client[settings.MONGODB_DB_NAME]

# Collections
users_collection = db.users
leaves_collection = db.leaves
leave_balances_collection = db.leave_balances
revoked_tokens_collection = db.revoked_tokens
oauth_states_collection = db.oauth_states


async def ping_database():
    await client.admin.command("ping")


async def create_indexes():
    """Create required indexes on startup."""
    # Unique email index
    await users_collection.create_index("email", unique=True)

    # Leave queries
    await leaves_collection.create_index("employee_id")
    await leaves_collection.create_index("status")

    # Balance lookups
    await leave_balances_collection.create_index(
        [("employee_id", 1), ("year", 1)], unique=True
    )

    # Revoked tokens — TTL: auto-delete after 8 hours (match token expiry)
    await revoked_tokens_collection.create_index("jti", unique=True)
    await revoked_tokens_collection.create_index(
        "revoked_at", expireAfterSeconds=8 * 3600
    )

    # OAuth states — TTL: auto-delete after 10 minutes
    await oauth_states_collection.create_index("nonce", unique=True)
    await oauth_states_collection.create_index(
        "created_at", expireAfterSeconds=600
    )

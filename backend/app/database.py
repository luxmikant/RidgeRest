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


async def ping_database():
    await client.admin.command("ping")


async def create_indexes():
    """Create required indexes on startup."""
    # Users: unique email + clerk_id
    await users_collection.create_index("email", unique=True, sparse=True)
    await users_collection.create_index("clerk_id", unique=True, sparse=True)

    # Leave queries
    await leaves_collection.create_index("employee_id")
    await leaves_collection.create_index("status")

    # Balance lookups
    await leave_balances_collection.create_index(
        [("employee_id", 1), ("year", 1)], unique=True
    )


import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.core.security import require_employer
from app.database import leaves_collection, users_collection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
async def get_analytics_overview(user: dict = Depends(require_employer)):
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month

    # Total counts by status
    status_pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    status_counts = {}
    async for doc in leaves_collection.aggregate(status_pipeline):
        status_counts[doc["_id"]] = doc["count"]

    # Leaves by type
    type_pipeline = [
        {"$group": {"_id": "$leave_type", "count": {"$sum": 1}}}
    ]
    type_counts = {}
    async for doc in leaves_collection.aggregate(type_pipeline):
        type_counts[doc["_id"]] = doc["count"]

    # Monthly breakdown (current year) — group by month from start_date
    monthly_pipeline = [
        {
            "$addFields": {
                "month": {
                    "$month": {"$dateFromString": {"dateString": "$start_date"}}
                },
                "year": {
                    "$year": {"$dateFromString": {"dateString": "$start_date"}}
                },
            }
        },
        {"$match": {"year": year}},
        {
            "$group": {
                "_id": {"month": "$month", "status": "$status"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id.month": 1}},
    ]
    monthly_data = []
    async for doc in leaves_collection.aggregate(monthly_pipeline):
        monthly_data.append(
            {
                "month": doc["_id"]["month"],
                "status": doc["_id"]["status"],
                "count": doc["count"],
            }
        )

    # Top employees by leave count
    top_pipeline = [
        {"$group": {"_id": "$employee_id", "name": {"$first": "$employee_name"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    top_employees = []
    async for doc in leaves_collection.aggregate(top_pipeline):
        top_employees.append(
            {"employee_id": doc["_id"], "name": doc["name"], "count": doc["count"]}
        )

    # Total employees
    total_employees = await users_collection.count_documents({"role": "employee"})

    return {
        "status_counts": status_counts,
        "type_counts": type_counts,
        "monthly_data": monthly_data,
        "top_employees": top_employees,
        "total_employees": total_employees,
    }

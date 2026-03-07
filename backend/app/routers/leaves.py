import logging
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import require_employee, require_employer
from app.database import leave_balances_collection, leaves_collection
from app.schemas.leave import (
    LeaveApply,
    LeaveReject,
    LeaveResponse,
    LeaveStatusEnum,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/leaves", tags=["leaves"])


def _leave_response(doc: dict) -> LeaveResponse:
    return LeaveResponse(
        id=str(doc["_id"]),
        employee_id=doc["employee_id"],
        employee_name=doc["employee_name"],
        leave_type=doc["leave_type"],
        start_date=doc["start_date"],
        end_date=doc["end_date"],
        reason=doc["reason"],
        status=doc["status"],
        rejection_reason=doc.get("rejection_reason"),
        created_at=doc["created_at"],
        updated_at=doc.get("updated_at"),
    )


def _count_days(start_date, end_date) -> int:
    """Count business days (weekdays) between two dates, inclusive."""
    from datetime import timedelta

    days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Mon-Fri
            days += 1
        current += timedelta(days=1)
    return days


# ─── Employee Endpoints ─────────────────────────────────────────────────

@router.post("/", response_model=LeaveResponse)
async def apply_leave(data: LeaveApply, user: dict = Depends(require_employee)):
    # Check for overlapping leave requests (pending or approved)
    overlap = await leaves_collection.find_one(
        {
            "employee_id": user["id"],
            "status": {"$in": ["pending", "approved"]},
            "start_date": {"$lte": data.end_date.isoformat()},
            "end_date": {"$gte": data.start_date.isoformat()},
        }
    )
    if overlap:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a leave request overlapping these dates",
        )

    # Check balance
    year = data.start_date.year
    balance = await leave_balances_collection.find_one(
        {"employee_id": user["id"], "year": year}
    )
    if balance:
        type_balance = balance.get(data.leave_type.value, {})
        remaining = type_balance.get("total", 0) - type_balance.get("used", 0)
        days_requested = _count_days(data.start_date, data.end_date)
        if days_requested > remaining:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient {data.leave_type.value} leave balance. Remaining: {remaining}, Requested: {days_requested}",
            )

    leave_doc = {
        "employee_id": user["id"],
        "employee_name": user["name"],
        "leave_type": data.leave_type.value,
        "start_date": data.start_date.isoformat(),
        "end_date": data.end_date.isoformat(),
        "reason": data.reason,
        "status": "pending",
        "rejection_reason": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
    }

    result = await leaves_collection.insert_one(leave_doc)
    leave_doc["_id"] = result.inserted_id

    logger.info("Leave applied: employee=%s type=%s", user["id"], data.leave_type.value)
    return _leave_response(leave_doc)


@router.get("/my", response_model=list[LeaveResponse])
async def get_my_leaves(
    status_filter: str = Query(None, alias="status"),
    user: dict = Depends(require_employee),
):
    query = {"employee_id": user["id"]}
    if status_filter:
        query["status"] = status_filter

    cursor = leaves_collection.find(query).sort("created_at", -1)
    leaves = await cursor.to_list(length=100)
    return [_leave_response(l) for l in leaves]


@router.delete("/{leave_id}")
async def cancel_leave(leave_id: str, user: dict = Depends(require_employee)):
    try:
        oid = ObjectId(leave_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid leave ID")

    leave = await leaves_collection.find_one({"_id": oid})
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    if leave["employee_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not your leave request")

    if leave["status"] != "pending":
        raise HTTPException(
            status_code=400, detail="Can only cancel pending leave requests"
        )

    await leaves_collection.delete_one({"_id": oid})
    logger.info("Leave cancelled: %s by employee=%s", leave_id, user["id"])
    return {"message": "Leave request cancelled"}


# ─── Employer Endpoints ─────────────────────────────────────────────────

@router.get("/", response_model=list[LeaveResponse])
async def get_all_leaves(
    status_filter: str = Query(None, alias="status"),
    employee_id: str = Query(None),
    user: dict = Depends(require_employer),
):
    query: dict = {}
    if status_filter:
        query["status"] = status_filter
    if employee_id:
        query["employee_id"] = employee_id

    cursor = leaves_collection.find(query).sort("created_at", -1)
    leaves = await cursor.to_list(length=200)
    return [_leave_response(l) for l in leaves]


@router.patch("/{leave_id}/approve", response_model=LeaveResponse)
async def approve_leave(leave_id: str, user: dict = Depends(require_employer)):
    try:
        oid = ObjectId(leave_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid leave ID")

    leave = await leaves_collection.find_one({"_id": oid})
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    if leave["status"] != "pending":
        raise HTTPException(status_code=400, detail="Leave is not in pending status")

    # Deduct from balance
    days = _count_days(
        __import__("datetime").date.fromisoformat(leave["start_date"]),
        __import__("datetime").date.fromisoformat(leave["end_date"]),
    )
    leave_type = leave["leave_type"]
    year = int(leave["start_date"][:4])

    await leave_balances_collection.update_one(
        {"employee_id": leave["employee_id"], "year": year},
        {"$inc": {f"{leave_type}.used": days}},
    )

    now = datetime.now(timezone.utc)
    await leaves_collection.update_one(
        {"_id": oid}, {"$set": {"status": "approved", "updated_at": now}}
    )

    leave["status"] = "approved"
    leave["updated_at"] = now

    logger.info("Leave approved: %s by employer=%s", leave_id, user["id"])

    # Emit socket event
    try:
        from app.socket_manager import sio
        await sio.emit(
            "leave_status_changed",
            {"leave_id": leave_id, "status": "approved", "employee_id": leave["employee_id"]},
            room=leave["employee_id"],
        )
    except Exception:
        pass  # Socket not critical

    return _leave_response(leave)


@router.patch("/{leave_id}/reject", response_model=LeaveResponse)
async def reject_leave(
    leave_id: str, data: LeaveReject, user: dict = Depends(require_employer)
):
    try:
        oid = ObjectId(leave_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid leave ID")

    leave = await leaves_collection.find_one({"_id": oid})
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    if leave["status"] != "pending":
        raise HTTPException(status_code=400, detail="Leave is not in pending status")

    now = datetime.now(timezone.utc)
    await leaves_collection.update_one(
        {"_id": oid},
        {
            "$set": {
                "status": "rejected",
                "rejection_reason": data.rejection_reason,
                "updated_at": now,
            }
        },
    )

    leave["status"] = "rejected"
    leave["rejection_reason"] = data.rejection_reason
    leave["updated_at"] = now

    logger.info("Leave rejected: %s by employer=%s", leave_id, user["id"])

    # Emit socket event
    try:
        from app.socket_manager import sio
        await sio.emit(
            "leave_status_changed",
            {
                "leave_id": leave_id,
                "status": "rejected",
                "rejection_reason": data.rejection_reason,
                "employee_id": leave["employee_id"],
            },
            room=leave["employee_id"],
        )
    except Exception:
        pass

    return _leave_response(leave)

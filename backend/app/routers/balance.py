import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import require_employee, require_employer
from app.database import leave_balances_collection
from app.schemas.leave import LeaveBalanceResponse, BalanceDetail

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/balance", tags=["balance"])


def _balance_response(doc: dict) -> LeaveBalanceResponse:
    return LeaveBalanceResponse(
        employee_id=doc["employee_id"],
        year=doc["year"],
        sick=BalanceDetail(**doc["sick"]),
        casual=BalanceDetail(**doc["casual"]),
        annual=BalanceDetail(**doc["annual"]),
    )


@router.get("/", response_model=LeaveBalanceResponse)
async def get_my_balance(user: dict = Depends(require_employee)):
    year = datetime.now(timezone.utc).year
    balance = await leave_balances_collection.find_one(
        {"employee_id": user["id"], "year": year}
    )
    if not balance:
        # Auto-init
        balance = {
            "employee_id": user["id"],
            "year": year,
            "sick": {"total": 10, "used": 0},
            "casual": {"total": 10, "used": 0},
            "annual": {"total": 15, "used": 0},
        }
        await leave_balances_collection.insert_one(balance)

    return _balance_response(balance)


@router.get("/{employee_id}", response_model=LeaveBalanceResponse)
async def get_employee_balance(
    employee_id: str, user: dict = Depends(require_employer)
):
    year = datetime.now(timezone.utc).year
    balance = await leave_balances_collection.find_one(
        {"employee_id": employee_id, "year": year}
    )
    if not balance:
        raise HTTPException(status_code=404, detail="Balance not found for this employee")

    return _balance_response(balance)

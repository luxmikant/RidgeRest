from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class LeaveTypeEnum(str, Enum):
    sick = "sick"
    casual = "casual"
    annual = "annual"


class LeaveStatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class LeaveApply(BaseModel):
    leave_type: LeaveTypeEnum
    start_date: date
    end_date: date
    reason: str = Field(..., min_length=10, max_length=500)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be >= start_date")
        if self.start_date < date.today():
            raise ValueError("start_date cannot be in the past")
        return self


class LeaveReject(BaseModel):
    rejection_reason: str = Field(..., min_length=5, max_length=500)


class LeaveResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: str
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    status: str
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class BalanceDetail(BaseModel):
    total: int
    used: int

    @property
    def remaining(self) -> int:
        return self.total - self.used


class LeaveBalanceResponse(BaseModel):
    employee_id: str
    year: int
    sick: BalanceDetail
    casual: BalanceDetail
    annual: BalanceDetail

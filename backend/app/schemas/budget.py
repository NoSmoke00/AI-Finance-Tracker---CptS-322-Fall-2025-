from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class BudgetPeriod(str, Enum):
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    YEARLY = "yearly"


class BudgetBase(BaseModel):
    category: str
    amount: float
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    is_active: bool = True
    alert_threshold: float = 80.0


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    amount: Optional[float] = None
    period: Optional[BudgetPeriod] = None
    is_active: Optional[bool] = None
    alert_threshold: Optional[float] = None


class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BudgetStatusResponse(BudgetResponse):
    spent: float
    remaining: float
    percentage_used: float
    is_over_budget: bool
    is_near_threshold: bool

    class Config:
        from_attributes = True


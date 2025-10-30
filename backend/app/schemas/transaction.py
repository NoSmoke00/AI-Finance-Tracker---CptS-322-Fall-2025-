from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


class TransactionBase(BaseModel):
    amount: float
    date: date
    name: str
    merchant_name: Optional[str] = None
    category: Optional[List[str]] = None
    primary_category: Optional[str] = None
    pending: Optional[bool] = False
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    user_id: int
    account_id: int
    plaid_transaction_id: Optional[str] = None


class TransactionUpdate(BaseModel):
    name: Optional[str] = None
    merchant_name: Optional[str] = None
    category: Optional[List[str]] = None
    primary_category: Optional[str] = None
    pending: Optional[bool] = None
    notes: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    account_id: int
    plaid_transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TransactionSummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_savings: float
    transaction_count: int
    by_category: List[dict]



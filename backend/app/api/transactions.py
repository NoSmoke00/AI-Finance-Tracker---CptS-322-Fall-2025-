from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models import Transaction, Account, User
from app.auth.router import get_current_user_dependency
from app.schemas.transaction import (
    TransactionResponse,
    TransactionSummaryResponse,
)
from app.services.transaction_service import sync_transactions_for_user, get_transaction_summary


router = APIRouter()


@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = Query(50, le=200),
    account_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
):
    q = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    if account_id is not None:
        q = q.filter(Transaction.account_id == account_id)
    if start_date is not None:
        q = q.filter(Transaction.date >= start_date)
    if end_date is not None:
        q = q.filter(Transaction.date <= end_date)
    if category is not None:
        q = q.filter(Transaction.primary_category == category)
    if search:
        ilike = f"%{search}%"
        q = q.filter((Transaction.name.ilike(ilike)) | (Transaction.merchant_name.ilike(ilike)))

    q = q.order_by(Transaction.date.desc(), Transaction.id.desc())
    return q.offset(skip).limit(limit).all()


 


@router.post("/sync")
def sync_transactions(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
):
    result = sync_transactions_for_user(current_user.id, db)
    return {"message": "Sync complete", **result}


@router.get("/summary", response_model=TransactionSummaryResponse)
def transactions_summary(
    period: str = Query(default='month'),
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
):
    # Normalize period
    allowed = {"day", "week", "month", "quarter", "year"}
    if period not in allowed:
        period = "month"
    # Determine date range by period
    today = date.today()
    if period == "day":
        start = today
    elif period == "week":
        start = date.fromordinal(today.toordinal() - 6)
    elif period == "month":
        start = date.fromordinal(today.toordinal() - 29)
    elif period == "quarter":
        start = date.fromordinal(today.toordinal() - 89)
    else:
        start = date.fromordinal(today.toordinal() - 364)

    summary = get_transaction_summary(current_user.id, db, start_date=start, end_date=today)
    return summary


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
):
    tx = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id,
    ).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.models import User, Account
from app.auth.router import get_current_user_dependency

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get dashboard summary with account balances and transaction totals."""
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    
    total_balance = 0
    account_summary = []
    
    for account in accounts:
        balance = float(account.balance_current) if account.balance_current else 0
        total_balance += balance
        
        account_summary.append({
            "id": account.id,
            "account_id": account.account_id,
            "name": account.name,
            "official_name": account.official_name,
            "type": account.type,
            "subtype": account.subtype,
            "mask": account.mask,
            "balance_current": balance,
            "balance_available": float(account.balance_available) if account.balance_available else 0,
            "currency_code": account.currency_code,
            "institution_name": account.plaid_item.institution_name
        })
    
    # Calculate summary statistics
    checking_balance = sum(
        float(acc.balance_current) if acc.balance_current else 0 
        for acc in accounts 
        if acc.subtype == "checking"
    )
    
    savings_balance = sum(
        float(acc.balance_current) if acc.balance_current else 0 
        for acc in accounts 
        if acc.subtype == "savings"
    )
    
    credit_balance = sum(
        float(acc.balance_current) if acc.balance_current else 0 
        for acc in accounts 
        if acc.type == "credit"
    )
    
    return {
        "user": {
            "name": f"{current_user.first_name} {current_user.last_name}",
            "email": current_user.email
        },
        "summary": {
            "total_balance": total_balance,
            "checking_balance": checking_balance,
            "savings_balance": savings_balance,
            "credit_balance": credit_balance,
            "total_accounts": len(accounts)
        },
        "accounts": account_summary
    }

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.auth.router import get_current_user_dependency
from app.models import User, Budget
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetStatusResponse, BudgetPeriod
from app.services.budget_service import BudgetService


router = APIRouter()
budget_service = BudgetService()


@router.get("/", response_model=List[BudgetResponse])
def list_budgets(
    active_only: bool = True,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get all budgets for the current user."""
    return budget_service.get_budgets(current_user.id, db, active_only=active_only)


@router.get("/status", response_model=List[BudgetStatusResponse])
def get_budgets_status(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get status for all active budgets including spending and progress."""
    budgets_with_status = budget_service.get_all_budget_statuses(current_user.id, db)
    
    # Convert to response format
    result = []
    for status in budgets_with_status:
        if status:
            budget = status["budget"]
            result.append(BudgetStatusResponse(
                id=budget.id,
                user_id=budget.user_id,
                category=budget.category,
                amount=float(budget.amount),
                period=budget.period.value if hasattr(budget.period, 'value') else budget.period,
                is_active=budget.is_active,
                alert_threshold=float(budget.alert_threshold) if budget.alert_threshold else 80.0,
                created_at=budget.created_at,
                updated_at=budget.updated_at,
                spent=status["spent"],
                remaining=status["remaining"],
                percentage_used=round(status["percentage_used"], 2),
                is_over_budget=status["is_over_budget"],
                is_near_threshold=status["is_near_threshold"]
            ))
    
    return result


@router.get("/{budget_id}/status", response_model=BudgetStatusResponse)
def get_budget_status(
    budget_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get status for a specific budget."""
    status = budget_service.get_budget_status(current_user.id, budget_id, db)
    
    if not status:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    budget = status["budget"]
    return BudgetStatusResponse(
        id=budget.id,
        user_id=budget.user_id,
        category=budget.category,
        amount=float(budget.amount),
        period=budget.period.value if hasattr(budget.period, 'value') else budget.period,
        is_active=budget.is_active,
        alert_threshold=float(budget.alert_threshold) if budget.alert_threshold else 80.0,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
        spent=status["spent"],
        remaining=status["remaining"],
        percentage_used=round(status["percentage_used"], 2),
        is_over_budget=status["is_over_budget"],
        is_near_threshold=status["is_near_threshold"]
    )


@router.post("/", response_model=BudgetResponse)
def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Create a new budget."""
    try:
        budget = budget_service.create_budget(
            user_id=current_user.id,
            category=budget_data.category,
            amount=budget_data.amount,
            period=budget_data.period,
            alert_threshold=budget_data.alert_threshold,
            db=db
        )
        return BudgetResponse(
            id=budget.id,
            user_id=budget.user_id,
            category=budget.category,
            amount=float(budget.amount),
            period=budget.period.value if hasattr(budget.period, 'value') else budget.period,
            is_active=budget.is_active,
            alert_threshold=float(budget.alert_threshold) if budget.alert_threshold else 80.0,
            created_at=budget.created_at,
            updated_at=budget.updated_at
        )
    except Exception as e:
        import traceback
        print(f"Error creating budget: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget_update: BudgetUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Update an existing budget."""
    budget = budget_service.update_budget(
        user_id=current_user.id,
        budget_id=budget_id,
        amount=budget_update.amount,
        period=budget_update.period,
        is_active=budget_update.is_active,
        alert_threshold=budget_update.alert_threshold,
        db=db
    )
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        category=budget.category,
        amount=float(budget.amount),
        period=budget.period.value if hasattr(budget.period, 'value') else budget.period,
        is_active=budget.is_active,
        alert_threshold=float(budget.alert_threshold) if budget.alert_threshold else 80.0,
        created_at=budget.created_at,
        updated_at=budget.updated_at
    )


@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Delete a budget (soft delete)."""
    success = budget_service.delete_budget(current_user.id, budget_id, db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return {"status": "ok", "message": "Budget deleted successfully"}


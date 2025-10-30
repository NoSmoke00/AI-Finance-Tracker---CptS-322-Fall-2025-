from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models import Budget, Transaction, BudgetPeriod


class BudgetService:
    def __init__(self):
        pass

    def get_budgets(self, user_id: int, db: Session, active_only: bool = True) -> List[Budget]:
        """Get all budgets for a user."""
        query = db.query(Budget).filter(Budget.user_id == user_id)
        if active_only:
            query = query.filter(Budget.is_active == True)  # noqa: E712
        return query.all()

    def get_budget_status(
        self,
        user_id: int,
        budget_id: int,
        db: Session
    ) -> Dict[str, any]:
        """Get the status of a budget including spent amount and progress."""
        budget = db.query(Budget).filter(
            Budget.id == budget_id,
            Budget.user_id == user_id
        ).first()

        if not budget:
            return None

        # Calculate date range based on budget period
        start_date, end_date = self._get_period_dates(budget.period)

        # Calculate spending for this category in the period
        spent = self._calculate_category_spending(
            user_id=user_id,
            category=budget.category,
            start_date=start_date,
            end_date=end_date,
            db=db
        )

        budget_amount = float(budget.amount)
        remaining = max(0, budget_amount - spent)
        percentage_used = (spent / budget_amount * 100) if budget_amount > 0 else 0
        is_over_budget = spent > budget_amount
        is_near_threshold = percentage_used >= float(budget.alert_threshold)

        return {
            "budget": budget,
            "spent": spent,
            "remaining": remaining,
            "percentage_used": percentage_used,
            "is_over_budget": is_over_budget,
            "is_near_threshold": is_near_threshold,
            "period_start": start_date,
            "period_end": end_date,
        }

    def get_all_budget_statuses(
        self,
        user_id: int,
        db: Session
    ) -> List[Dict[str, any]]:
        """Get status for all active budgets."""
        budgets = self.get_budgets(user_id, db, active_only=True)
        return [self.get_budget_status(user_id, budget.id, db) for budget in budgets]

    def _get_period_dates(self, period: BudgetPeriod) -> tuple:
        """Get start and end dates for the current budget period."""
        now = datetime.utcnow()
        today = now.date()

        if period == BudgetPeriod.WEEKLY:
            # Start of current week (Monday)
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday)
            end_date = start_date + timedelta(days=6)
        elif period == BudgetPeriod.YEARLY:
            # Current year
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        else:  # MONTHLY
            # Current month
            start_date = today.replace(day=1)
            # Next month minus one day
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        return start_date, end_date

    def _calculate_category_spending(
        self,
        user_id: int,
        category: str,
        start_date,
        end_date,
        db: Session
    ) -> float:
        """Calculate total spending for a category in a date range."""
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.primary_category == category,
            Transaction.amount < 0  # Only expenses
        ).all()

        return sum(abs(float(t.amount)) for t in transactions)

    def create_budget(
        self,
        user_id: int,
        category: str,
        amount: float,
        period: BudgetPeriod,
        db: Session,
        alert_threshold: float = 80.0
    ) -> Budget:
        """Create a new budget."""
        budget = Budget(
            user_id=user_id,
            category=category,
            amount=amount,
            period=period,
            alert_threshold=alert_threshold,
            is_active=True
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return budget

    def update_budget(
        self,
        user_id: int,
        budget_id: int,
        db: Session,
        amount: Optional[float] = None,
        period: Optional[BudgetPeriod] = None,
        is_active: Optional[bool] = None,
        alert_threshold: Optional[float] = None
    ) -> Budget:
        """Update an existing budget."""
        budget = db.query(Budget).filter(
            Budget.id == budget_id,
            Budget.user_id == user_id
        ).first()

        if not budget:
            return None

        if amount is not None:
            budget.amount = amount
        if period is not None:
            budget.period = period
        if is_active is not None:
            budget.is_active = is_active
        if alert_threshold is not None:
            budget.alert_threshold = alert_threshold

        budget.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(budget)
        return budget

    def delete_budget(self, user_id: int, budget_id: int, db: Session) -> bool:
        """Delete a budget (soft delete by setting is_active=False)."""
        budget = db.query(Budget).filter(
            Budget.id == budget_id,
            Budget.user_id == user_id
        ).first()

        if not budget:
            return False

        budget.is_active = False
        budget.updated_at = datetime.utcnow()
        db.commit()
        return True


import os
from datetime import datetime, timedelta, date
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from app.models import Transaction, Account, Insight


class InsightsAI:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

    def _build_analysis_prompt(
        self,
        user_id: int,
        db: Session,
        start_date: date,
        end_date: date,
    ) -> str:
        # Aggregate data for prompt
        txs: List[Transaction] = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        ).all()

        # Signed aggregates (not sent to model to avoid polarity confusion)
        by_category: Dict[str, float] = {}
        by_merchant: Dict[str, float] = {}
        expense_by_category: Dict[str, float] = {}
        income_by_category: Dict[str, float] = {}
        expense_by_merchant: Dict[str, float] = {}
        income_by_merchant: Dict[str, float] = {}
        large_txs: List[Dict[str, Any]] = []
        total_expense = 0.0
        total_income = 0.0
        for t in txs:
            cat = t.primary_category or "Uncategorized"
            by_category[cat] = by_category.get(cat, 0.0) + float(t.amount)
            m = (t.merchant_name or t.name) or "Unknown"
            by_merchant[m] = by_merchant.get(m, 0.0) + float(t.amount)
            if t.amount < 0:
                expense_by_category[cat] = expense_by_category.get(cat, 0.0) + abs(float(t.amount))
                expense_by_merchant[m] = expense_by_merchant.get(m, 0.0) + abs(float(t.amount))
                total_expense += abs(float(t.amount))
            elif t.amount > 0:
                income_by_category[cat] = income_by_category.get(cat, 0.0) + float(t.amount)
                income_by_merchant[m] = income_by_merchant.get(m, 0.0) + float(t.amount)
                total_income += float(t.amount)
            if abs(float(t.amount)) >= 100:
                large_txs.append({
                    "date": t.date.isoformat(),
                    "name": t.name,
                    "merchant": t.merchant_name,
                    "amount": float(t.amount),
                    "amount_abs": abs(float(t.amount)),
                    "direction": "expense" if float(t.amount) < 0 else ("income" if float(t.amount) > 0 else "neutral"),
                    "category": t.primary_category,
                })

        prompt = {
            "instruction": "Analyze user's finances and produce up to 8 high-priority, non-duplicative JSON insights. Avoid repeating the same merchant/topic; consolidate duplicates.",
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "totals": {"expense": total_expense, "income": total_income},
            "expense_by_category": expense_by_category,
            "income_by_category": income_by_category,
            "expense_by_merchant": expense_by_merchant,
            "income_by_merchant": income_by_merchant,
            "large_transactions": large_txs[:50],
            "polarity_note": "Amounts use accounting polarity: negative = expense/cash outflow, positive = income/cash inflow. When reporting amounts in insights, present magnitudes as positive dollars and clearly state expense vs income.",
            "return_format": [
                {
                    "type": "alert|warning|info|success|tip",
                    "title": "string",
                    "description": "string",
                    "action": "string|optional",
                    "amount": "number|optional (positive magnitude)",
                    "category": "string|optional",
                    "priority": "1-10"
                }
            ],
            "considerations": [
                "spending anomalies",
                "budget alerts",
                "recurring charges",
                "trends",
                "savings opportunities",
                "positive patterns",
                "duplicate charges",
                "unusual merchants"
            ],
        }
        import json
        return json.dumps(prompt)

    def _call_groq(self, prompt: str) -> List[Dict[str, Any]]:
        # Lazy import; handle missing API key by returning empty
        if not self.api_key:
            return []
        try:
            from groq import Groq
            client = Groq(api_key=self.api_key)
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a finance insights generator that outputs ONLY JSON array."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1200,
            )
            content = completion.choices[0].message.content or "[]"
            import json
            data = json.loads(content)
            if isinstance(data, dict) and "insights" in data:
                return data["insights"]
            if isinstance(data, list):
                return data
            return []
        except Exception:
            return []

    def generate_insights_for_user(self, user_id: int, db: Session) -> List[Insight]:
        end_date = datetime.utcnow().date()
        start_date = (datetime.utcnow() - timedelta(days=90)).date()
        prompt = self._build_analysis_prompt(user_id, db, start_date, end_date)
        ai_results = self._call_groq(prompt)

        insights: List[Insight] = []

        # Fallback heuristic if AI not available or empty
        if not ai_results:
            # Simple heuristic: if spending in any category < -500 in last 30d, raise warning
            last30_start = (datetime.utcnow() - timedelta(days=30)).date()
            txs = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.date >= last30_start,
                Transaction.date <= end_date,
            ).all()
            by_cat: Dict[str, float] = {}
            for t in txs:
                cat = t.primary_category or "Uncategorized"
                by_cat[cat] = by_cat.get(cat, 0.0) + float(t.amount)
            for cat, amt in by_cat.items():
                if amt < -500:
                    insights.append(Insight(
                        user_id=user_id,
                        type="warning",
                        title=f"High spending in {cat}",
                        description=f"You've spent {abs(amt):.2f} in {cat} over the past 30 days.",
                        amount=abs(amt),
                        category=cat,
                        priority=7,
                    ))
        else:
            for item in ai_results[:10]:
                try:
                    insights.append(Insight(
                        user_id=user_id,
                        type=str(item.get("type", "info")),
                        title=str(item.get("title", "Insight")),
                        description=str(item.get("description", "")),
                        action=None,
                        amount=float(item.get("amount")) if item.get("amount") is not None else None,
                        category=item.get("category"),
                        priority=int(item.get("priority", 5)),
                        data=item,
                    ))
                except Exception:
                    continue

        # De-duplicate and prioritize before persisting
        # Key by (normalized title, category)
        norm = lambda s: (s or "").strip().lower()
        dedup: Dict[tuple, Insight] = {}
        for ins in insights:
            key = (norm(ins.title), norm(ins.category))
            if key not in dedup:
                dedup[key] = ins
            else:
                # keep higher priority or larger amount
                a = dedup[key]
                if (ins.priority or 0) > (a.priority or 0):
                    dedup[key] = ins
                elif (ins.priority or 0) == (a.priority or 0):
                    if (abs(ins.amount or 0.0)) > (abs(a.amount or 0.0)):
                        dedup[key] = ins

        # Sort by priority desc then amount magnitude desc
        sorted_list = sorted(dedup.values(), key=lambda x: ((x.priority or 0), abs(x.amount or 0.0)), reverse=True)

        # Limit total and limit per type to reduce overwhelm
        max_total = 8
        max_per_type = 3
        picked: List[Insight] = []
        per_type_count: Dict[str, int] = {}
        for ins in sorted_list:
            t = (ins.type or "info").lower()
            if per_type_count.get(t, 0) >= max_per_type:
                continue
            picked.append(ins)
            per_type_count[t] = per_type_count.get(t, 0) + 1
            if len(picked) >= max_total:
                break

        # Persist only picked
        saved: List[Insight] = []
        for ins in picked:
            db.add(ins)
        db.commit()
        for ins in picked:
            db.refresh(ins)
            saved.append(ins)

        saved.sort(key=lambda x: (x.priority or 0, x.created_at or datetime.utcnow()), reverse=True)
        return saved

    def get_active_insights(self, user_id: int, db: Session) -> List[Insight]:
        now = datetime.utcnow()
        q = db.query(Insight).filter(
            Insight.user_id == user_id,
            Insight.dismissed == False,  # noqa: E712
        )
        q = q.filter((Insight.expires_at.is_(None)) | (Insight.expires_at > now))
        return q.order_by(Insight.priority.desc(), Insight.created_at.desc()).all()



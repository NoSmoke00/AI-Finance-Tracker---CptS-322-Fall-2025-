import os
from datetime import datetime, timedelta, date
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from app.models import Transaction, Account, Insight, Budget


class InsightsAI:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        # Config similar to prior project
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.temperature_financial = float(os.getenv("GROQ_TEMP_FINANCIAL", "0.3"))
        self.temperature_insights = float(os.getenv("GROQ_TEMP_INSIGHTS", "0.5"))
        self.max_tokens_insights = int(os.getenv("GROQ_MAX_TOKENS_INSIGHTS", "1200"))
        self.retries = int(os.getenv("GROQ_RETRIES", "3"))
        self.retry_delay_ms = int(os.getenv("GROQ_RETRY_DELAY_MS", "1000"))

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

        # Build last-30-days expense transaction slice (amount magnitudes, capped to 50)
        last30_start = (datetime.utcnow() - timedelta(days=30)).date()
        expense_txs_last30 = [
            {
                "date": t.date.isoformat(),
                "name": t.name,
                "merchant": t.merchant_name,
                "category": t.primary_category or "Uncategorized",
                "amount": abs(float(t.amount)),  # magnitude
            }
            for t in txs
            if (t.amount < 0 and t.date >= last30_start)
        ]
        expense_txs_last30 = sorted(expense_txs_last30, key=lambda x: x["date"], reverse=True)[:50]

        # Fetch budgets for this user
        budgets = db.query(Budget).filter(Budget.user_id == user_id, Budget.is_active == True).all()  # noqa: E712
        budgets_dict = {b.category: {"amount": float(b.amount), "period": b.period.value, "threshold": float(b.alert_threshold)} for b in budgets}

        prompt = {
            "instruction": (
                "You are a financial advisor AI. Analyze EXPENSE transactions only (income/deposits tracked separately). "
                "CRITICAL: In our data, amount<0 = expense, amount>0 = income. Use absolute magnitudes for expense amounts and clearly label as expense. "
                "Use provided expense_by_* and income_by_* aggregates. Avoid treating income as expense. Return ONLY a JSON array. "
                "Max 6 insights recommended; avoid repeating the same merchant/topic; consolidate duplicates."
            ),
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "totals": {"expense": total_expense, "income": total_income},
            "expense_by_category": expense_by_category,
            "income_by_category": income_by_category,
            "expense_by_merchant": expense_by_merchant,
            "income_by_merchant": income_by_merchant,
            "large_transactions": large_txs[:50],
            "expenses_last_30_days": expense_txs_last30,
            "budgets": budgets_dict,
            "polarity_note": "negative = expense/cash outflow; positive = income/cash inflow. Use expense magnitudes (positive numbers) when describing spending.",
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
                "budget alerts - compare expense_by_category against budgets for each category",
                "recurring charges",
                "trends",
                "savings opportunities",
                "positive patterns",
                "duplicate charges",
                "unusual merchants",
                "when category has a budget, calculate spending percentage vs budget and alert if near/exceeding threshold"
            ],
            "examples": [
                {
                    "type": "warning",
                    "title": "High expense in FOOD_AND_DRINK",
                    "description": "You spent $245 in FOOD_AND_DRINK over the past 30 days, 35% above your usual $180.",
                    "amount": 245,
                    "category": "FOOD_AND_DRINK",
                    "priority": 7
                },
                {
                    "type": "alert",
                    "title": "Recurring subscription: Spotify",
                    "description": "Detected a $9.99 monthly charge to Spotify recurring on the 15th.",
                    "amount": 9.99,
                    "category": "SUBSCRIPTIONS",
                    "priority": 8
                }
            ],
        }
        import json
        return json.dumps(prompt)

    def _clean_json_text(self, text: str) -> str:
        cleaned = (text or "").strip()
        if cleaned.startswith("```json") and cleaned.endswith("```"):
            return cleaned[7:-3].strip()
        if cleaned.startswith("```") and cleaned.endswith("```"):
            return cleaned[3:-3].strip()
        return cleaned

    def _call_groq_once(self, prompt: str) -> List[Dict[str, Any]]:
        # Lazy import; handle missing API key by returning empty
        if not self.api_key:
            return []
        try:
            from groq import Groq
            client = Groq(api_key=self.api_key)
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a finance insights generator that outputs ONLY JSON array."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature_financial,
                max_tokens=self.max_tokens_insights,
            )
            content = completion.choices[0].message.content or "[]"
            content = self._clean_json_text(content)
            import json
            data = json.loads(content)
            if isinstance(data, dict) and "insights" in data:
                return data["insights"]
            if isinstance(data, list):
                return data
            return []
        except Exception:
            return []

    def _call_groq(self, prompt: str) -> List[Dict[str, Any]]:
        # Retry with exponential backoff
        last: List[Dict[str, Any]] = []
        for attempt in range(self.retries + 1):
            result = self._call_groq_once(prompt)
            if result:
                return result
            if attempt == self.retries:
                break
            import time
            delay = (self.retry_delay_ms / 1000.0) * (2 ** attempt)
            time.sleep(delay)
        return last

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
            allowed_types = {"alert", "warning", "info", "success", "tip"}
            for item in ai_results[:50]:
                try:
                    t = str(item.get("type", "info")).lower()
                    if t not in allowed_types:
                        t = "info"
                    amt_raw = item.get("amount")
                    amt = float(amt_raw) if amt_raw is not None else None
                    if amt is not None:
                        amt = abs(amt)
                    insights.append(Insight(
                        user_id=user_id,
                        type=t,
                        title=str(item.get("title", "Insight")),
                        description=str(item.get("description", "")),
                        action=None,
                        amount=amt,
                        category=item.get("category"),
                        priority=int(item.get("priority", 5)),
                        data=item,
                    ))
                except Exception:
                    continue

        # De-duplicate and prioritize before persisting
        # Key by (type, normalized title sans numbers, category)
        def _norm_text(s: str) -> str:
            import re
            base = (s or "").strip().lower()
            base = re.sub(r"\d+(?:[\.,]\d+)?", "0", base)  # neutralize numbers
            base = re.sub(r"\s+", " ", base)
            return base
        dedup: Dict[tuple, Insight] = {}
        for ins in insights:
            key = ((ins.type or "info").lower(), _norm_text(ins.title or ""), (ins.category or "").strip().lower())
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

        # Limit total and limit per type (aim for 3-7 per type when available)
        max_total = 30
        per_type_caps = {"alert": 7, "warning": 7, "info": 7, "success": 7, "tip": 7}
        min_per_type = {"alert": 3, "warning": 3, "info": 3, "success": 3, "tip": 3}
        picked: List[Insight] = []
        per_type_count: Dict[str, int] = {}
        for ins in sorted_list:
            t = (ins.type or "info").lower()
            cap = per_type_caps.get(t, 1)
            if per_type_count.get(t, 0) >= cap:
                continue
            picked.append(ins)
            per_type_count[t] = per_type_count.get(t, 0) + 1
            if len(picked) >= max_total:
                break

        # Second pass: try to meet minimum per-type targets if more candidates exist
        if len(picked) < max_total:
            already = set(id(x) for x in picked)
            for t_key, min_needed in min_per_type.items():
                if per_type_count.get(t_key, 0) >= min_needed:
                    continue
                for ins in sorted_list:
                    if id(ins) in already:
                        continue
                    if (ins.type or "info").lower() != t_key:
                        continue
                    if per_type_count.get(t_key, 0) >= per_type_caps.get(t_key, 1):
                        break
                    picked.append(ins)
                    already.add(id(ins))
                    per_type_count[t_key] = per_type_count.get(t_key, 0) + 1
                    if per_type_count[t_key] >= min_needed or len(picked) >= max_total:
                        break

        # Prepare aggregates for heuristic gap-filler
        # Recompute aggregates in-scope for this function
        txs_agg = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        ).all()
        expense_by_category: Dict[str, float] = {}
        expense_by_merchant: Dict[str, float] = {}
        total_expense = 0.0
        for t in txs_agg:
            if float(t.amount) < 0:
                cat = (t.primary_category or "Uncategorized")
                m = (t.merchant_name or t.name) or "Unknown"
                val = abs(float(t.amount))
                expense_by_category[cat] = expense_by_category.get(cat, 0.0) + val
                expense_by_merchant[m] = expense_by_merchant.get(m, 0.0) + val
                total_expense += val

        # Heuristic gap-filler: if a type is still under the minimum and there is room,
        # synthesize simple, accurate insights from aggregates so users see 3–7 per type.
        if len(picked) < max_total:
            # Build helper lists from aggregates
            top_expense_cats = sorted(
                [(k, v) for k, v in expense_by_category.items()], key=lambda x: x[1], reverse=True
            )[:5]
            top_expense_merchants = sorted(
                [(k, v) for k, v in expense_by_merchant.items()], key=lambda x: x[1], reverse=True
            )[:5]

            def add_insight(t_type: str, title: str, desc: str, amount_val: float | None, category_val: str | None, priority_val: int):
                nonlocal picked, per_type_count
                if len(picked) >= max_total:
                    return
                if per_type_count.get(t_type, 0) >= per_type_caps.get(t_type, 1):
                    return
                picked.append(Insight(
                    user_id=user_id,
                    type=t_type,
                    title=title,
                    description=desc,
                    action=None,
                    amount=(abs(float(amount_val)) if amount_val is not None else None),
                    category=category_val,
                    priority=priority_val,
                    data={"source": "heuristic_gap_fill"},
                ))
                per_type_count[t_type] = per_type_count.get(t_type, 0) + 1

            for t_key, min_needed in min_per_type.items():
                while per_type_count.get(t_key, 0) < min_needed and len(picked) < max_total:
                    if t_key in ("alert", "warning") and top_expense_cats:
                        cat, val = top_expense_cats[per_type_count.get(t_key, 0) % len(top_expense_cats)]
                        add_insight(
                            t_key,
                            f"High expense in {cat}",
                            f"You spent ${val:.2f} in {cat} over the last 90 days.",
                            val,
                            cat,
                            7 if t_key == "warning" else 8,
                        )
                    elif t_key == "info" and top_expense_merchants:
                        m, val = top_expense_merchants[per_type_count.get(t_key, 0) % len(top_expense_merchants)]
                        add_insight(
                            t_key,
                            f"Top spending at {m}",
                            f"Total expense ${val:.2f} at {m} in the period.",
                            val,
                            None,
                            5,
                        )
                    elif t_key == "tip" and top_expense_cats:
                        cat, val = top_expense_cats[per_type_count.get(t_key, 0) % len(top_expense_cats)]
                        target = max(val * 0.8, 0.0)
                        add_insight(
                            t_key,
                            f"Savings opportunity in {cat}",
                            f"Consider reducing {cat} spend from ${val:.2f} to ${target:.2f} next month.",
                            val - target,
                            cat,
                            5,
                        )
                    elif t_key == "success" and total_expense >= 0:
                        add_insight(
                            t_key,
                            "Consistent tracking",
                            "Your recent expenses are being tracked consistently. Keep it up!",
                            None,
                            None,
                            4,
                        )
                    else:
                        break

        # Replace existing active insights for this user to avoid accumulation/duplicates
        db.query(Insight).filter(Insight.user_id == user_id, Insight.dismissed == False).delete(synchronize_session=False)  # noqa: E712

        # Enrich descriptions with period context and category deltas
        last30_start = (datetime.utcnow() - timedelta(days=30)).date()
        prev30_start = (datetime.utcnow() - timedelta(days=60)).date()
        prev30_end = (datetime.utcnow() - timedelta(days=31)).date()
        # Build category sums for last30 and prev30
        cat_last30: Dict[str, float] = {}
        cat_prev30: Dict[str, float] = {}
        txs_last60 = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.date >= prev30_start,
            Transaction.date <= end_date,
        ).all()
        for t in txs_last60:
            if float(t.amount) >= 0:
                continue
            cat = (t.primary_category or "Uncategorized")
            amt = abs(float(t.amount))
            if t.date >= last30_start:
                cat_last30[cat] = cat_last30.get(cat, 0.0) + amt
            elif t.date <= prev30_end:
                cat_prev30[cat] = cat_prev30.get(cat, 0.0) + amt

        for ins in picked:
            cat = ins.category or None
            if cat:
                v_now = cat_last30.get(cat, 0.0)
                v_prev = cat_prev30.get(cat, 0.0)
                delta = None
                if v_prev > 0:
                    delta = ((v_now - v_prev) / v_prev) * 100.0
                elif v_now > 0 and v_prev == 0:
                    delta = 100.0
                addendum = f" Period: {start_date.isoformat()} to {end_date.isoformat()}."
                if v_now > 0:
                    addendum += f" {cat} spend: ${v_now:.2f}"
                if delta is not None:
                    sign = "+" if delta >= 0 else ""
                    addendum += f" ({sign}{delta:.0f}% vs prior 30d)."
                ins.description = (ins.description or "").rstrip()
                if addendum not in ins.description:
                    ins.description = (ins.description + addendum).strip()

        # Sanitize wording: if the insight category is a spend category, avoid calling it "income"
        spend_primary_categories = {
            "FOOD_AND_DRINK", "TRAVEL", "TRANSPORTATION", "GENERAL_MERCHANDISE", "RENT_AND_UTILITIES",
            "ENTERTAINMENT", "HEALTHCARE", "PERSONAL_CARE", "HOME", "AUTO_AND_TRANSPORT", "BILLS",
            "GROCERIES", "SHOPPING", "LOAN_PAYMENTS", "RENT", "DINING", "SUBSCRIPTIONS"
        }
        for ins in picked:
            cat = (ins.category or "").upper()
            title = ins.title or ""
            desc = ins.description or ""
            if cat and cat in spend_primary_categories:
                # Normalize common income-like phrases to expense wording
                replacements = [
                    ("Income", "Expense"),
                    ("income", "expense"),
                    ("Received", "Spent"),
                    ("received", "spent"),
                    ("Earning", "Spending"),
                    ("earning", "spending"),
                    ("Earnings", "Spending"),
                    ("earnings", "spending"),
                ]
                for old, new in replacements:
                    title = title.replace(old, new)
                    desc = desc.replace(old, new)
                ins.title = title
                ins.description = desc

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



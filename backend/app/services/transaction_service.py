from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import Tuple, Dict, Any, List, Optional

from app.models import PlaidItem, Account, Transaction

from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.country_code import CountryCode
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
import os


PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")

if PLAID_ENV == "sandbox":
    host_url = "https://sandbox.plaid.com"
elif PLAID_ENV == "development":
    host_url = "https://development.plaid.com"
else:
    host_url = "https://production.plaid.com"

configuration = Configuration(
    host=host_url,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)
api_client = ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)


def _extract_primary_category(category_list: Optional[List[str]]) -> Optional[str]:
    if not category_list:
        return None
    return category_list[0]


def sync_transactions_for_user(user_id: int, db: Session) -> Dict[str, int]:
    """Sync last 90 days of transactions for all Plaid items belonging to the user.

    Returns a dict with counts of new and updated transactions.
    """
    start_date: date = (datetime.now() - timedelta(days=90)).date()
    end_date: date = datetime.now().date()

    items: List[PlaidItem] = db.query(PlaidItem).filter(PlaidItem.user_id == user_id).all()

    num_created = 0
    num_updated = 0

    for item in items:
        try:
            req = TransactionsGetRequest(
                access_token=item.access_token,
                start_date=start_date,
                end_date=end_date,
                options=TransactionsGetRequestOptions(
                    include_personal_finance_category=True
                ),
            )
            resp = plaid_client.transactions_get(req)

            accounts_by_plaid_id: Dict[str, Account] = {a.account_id: a for a in item.accounts}

            for tr in resp['transactions']:
                plaid_tx_id = tr['transaction_id']
                plaid_account_id = tr['account_id']
                account = accounts_by_plaid_id.get(plaid_account_id)
                if not account:
                    continue

                existing: Optional[Transaction] = db.query(Transaction).filter(
                    Transaction.plaid_transaction_id == plaid_tx_id
                ).first()

                amount = float(tr['amount'])
                # Plaid: positive is expense; store expenses as negative
                amount_to_store = -amount

                # Use Plaid Personal Finance Category when present (simple handling)
                pfc = tr.get('personal_finance_category')
                primary_category = None
                categories = tr.get('category')
                if isinstance(pfc, dict):
                    primary_category = pfc.get('primary') or None
                    detailed = pfc.get('detailed') or None
                    categories = [c for c in [primary_category, detailed] if c]

                # Coerce categories to clean list[str]
                if categories is None:
                    categories = []
                try:
                    categories = [str(c) for c in categories if c]
                except Exception:
                    categories = []
                if not primary_category:
                    primary_category = categories[0] if categories else None

                fields = {
                    'user_id': user_id,
                    'account_id': account.id,
                    'plaid_transaction_id': plaid_tx_id,
                    'amount': amount_to_store,
                    'date': tr['date'],
                    'name': tr['name'],
                    'merchant_name': tr.get('merchant_name'),
                    'category': categories,
                    'primary_category': primary_category or _extract_primary_category(categories),
                    'pending': tr.get('pending', False),
                }

                if existing:
                    for k, v in fields.items():
                        setattr(existing, k, v)
                    num_updated += 1
                else:
                    tx = Transaction(**fields)
                    db.add(tx)
                    num_created += 1

            db.commit()
        except Exception:
            db.rollback()
            continue

    return {"created": num_created, "updated": num_updated}


def get_transaction_summary(user_id: int, db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
    """Aggregate totals by income/expense and category for a period."""
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    txs: List[Transaction] = query.all()
    total_income = sum(t.amount for t in txs if t.amount > 0)
    total_expenses = sum(-t.amount for t in txs if t.amount < 0)
    net_savings = total_income - total_expenses

    by_category: Dict[str, float] = {}
    for t in txs:
        cat = t.primary_category or "Uncategorized"
        by_category[cat] = by_category.get(cat, 0.0) + float(t.amount)

    return {
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "net_savings": float(net_savings),
        "transaction_count": len(txs),
        "by_category": [{"category": k, "amount": float(v)} for k, v in by_category.items()],
    }



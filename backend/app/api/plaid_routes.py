from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
import os
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, PlaidItem, Account
from app.auth.router import get_current_user_dependency

# Pydantic models
class ExchangeTokenRequest(BaseModel):
    public_token: str

router = APIRouter()

# Plaid configuration
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")

# Determine the host URL based on environment
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
client = plaid_api.PlaidApi(api_client)

@router.post("/link_token")
async def create_link_token(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Create a link token for Plaid Link initialization."""
    try:
        request = LinkTokenCreateRequest(
            products=[Products('transactions'), Products('auth')],
            client_name="AI-Finance Tracker",
            country_codes=[CountryCode('US')],
            language='en',
            webhook='https://webhook.sample.com',
            user=LinkTokenCreateRequestUser(
                client_user_id=str(current_user.id)
            )
        )
        response = client.link_token_create(request)
        return {"link_token": response['link_token'], "expiration": response['expiration']}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/exchange_token")
async def exchange_public_token(
    request: ExchangeTokenRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Exchange public token for access token and store item."""
    try:
        # Exchange public token for access token
        exchange_request = ItemPublicTokenExchangeRequest(public_token=request.public_token)
        response = client.item_public_token_exchange(exchange_request)
        access_token = response['access_token']
        item_id = response['item_id']

        # Get item info
        item_request = plaid.model.item_get_request.ItemGetRequest(access_token=access_token)
        item_response = client.item_get(item_request)
        institution_id = item_response['item']['institution_id']

        # Get institution info
        institution_request = plaid.model.institutions_get_by_id_request.InstitutionsGetByIdRequest(
            institution_id=institution_id,
            country_codes=[CountryCode('US')]
        )
        institution_response = client.institutions_get_by_id(institution_request)
        institution_name = institution_response['institution']['name']

        # Store Plaid item in database
        plaid_item = PlaidItem(
            user_id=current_user.id,
            access_token=access_token,
            item_id=item_id,
            institution_id=institution_id,
            institution_name=institution_name
        )
        db.add(plaid_item)
        db.commit()
        db.refresh(plaid_item)

        # Fetch and store accounts
        await fetch_accounts(plaid_item.id, db)

        return {"message": "Successfully linked bank account", "item_id": item_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def fetch_accounts(plaid_item_id: int, db: Session):
    """Fetch accounts from Plaid and store in database."""
    plaid_item = db.query(PlaidItem).filter(PlaidItem.id == plaid_item_id).first()
    if not plaid_item:
        return

    try:
        request = AccountsGetRequest(access_token=plaid_item.access_token)
        response = client.accounts_get(request)
        
        for account_data in response['accounts']:
            # Check if account already exists
            existing_account = db.query(Account).filter(
                Account.account_id == account_data['account_id'],
                Account.user_id == plaid_item.user_id
            ).first()
            
            if not existing_account:
                account = Account(
                    user_id=plaid_item.user_id,
                    plaid_item_id=plaid_item_id,
                    account_id=account_data['account_id'],
                    name=account_data['name'],
                    official_name=account_data.get('official_name'),
                    type=str(account_data['type']),  # Convert enum to string
                    subtype=str(account_data.get('subtype')) if account_data.get('subtype') else None,  # Convert enum to string
                    mask=account_data.get('mask'),
                    balance_current=float(account_data['balances']['current']) if account_data['balances']['current'] else 0,
                    balance_available=float(account_data['balances']['available']) if account_data['balances']['available'] else 0,
                    currency_code=account_data['balances']['iso_currency_code']
                )
                db.add(account)
        
        db.commit()
    except Exception as e:
        print(f"Error fetching accounts: {e}")

@router.get("/accounts")
async def get_accounts(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get all linked accounts for the current user."""
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    
    account_list = []
    for account in accounts:
        account_list.append({
            "id": account.id,
            "account_id": account.account_id,
            "name": account.name,
            "official_name": account.official_name,
            "type": account.type,
            "subtype": account.subtype,
            "mask": account.mask,
            "balance_current": float(account.balance_current) if account.balance_current else 0,
            "balance_available": float(account.balance_available) if account.balance_available else 0,
            "currency_code": account.currency_code,
            "institution_name": account.plaid_item.institution_name
        })
    
    return {"accounts": account_list}

@router.get("/transactions")
async def get_transactions(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get recent transactions for all linked accounts."""
    plaid_items = db.query(PlaidItem).filter(PlaidItem.user_id == current_user.id).all()
    
    all_transactions = []
    for plaid_item in plaid_items:
        try:
            # Get transactions from the last 30 days
            start_date = (datetime.now() - timedelta(days=30)).date()
            end_date = datetime.now().date()
            
            request = TransactionsGetRequest(
                access_token=plaid_item.access_token,
                start_date=start_date,
                end_date=end_date
            )
            response = client.transactions_get(request)
            
            for transaction in response['transactions']:
                all_transactions.append({
                    "transaction_id": transaction['transaction_id'],
                    "account_id": transaction['account_id'],
                    "amount": -transaction['amount'],  # Invert sign: Plaid positive = expense, we want positive = income
                    "date": transaction['date'],
                    "name": transaction['name'],
                    "merchant_name": transaction.get('merchant_name'),
                    "category": transaction.get('category'),
                    "account_name": next(
                        (acc.name for acc in plaid_item.accounts if acc.account_id == transaction['account_id']),
                        "Unknown Account"
                    )
                })
        except Exception as e:
            print(f"Error fetching transactions for item {plaid_item.id}: {e}")
    
    # Sort by date (most recent first)
    all_transactions.sort(key=lambda x: x['date'], reverse=True)
    
    return {"transactions": all_transactions[:50]}  # Return last 50 transactions

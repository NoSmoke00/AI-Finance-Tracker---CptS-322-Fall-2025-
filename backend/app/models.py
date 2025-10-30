from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Date, Enum
import enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSONB

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    plaid_items = relationship("PlaidItem", back_populates="user")
    accounts = relationship("Account", back_populates="user")
    budgets = relationship("Budget", back_populates="user")

class PlaidItem(Base):
    __tablename__ = "plaid_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    access_token = Column(String, nullable=False)
    item_id = Column(String, unique=True, nullable=False)
    institution_id = Column(String, nullable=False)
    institution_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="plaid_items")
    accounts = relationship("Account", back_populates="plaid_item")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plaid_item_id = Column(Integer, ForeignKey("plaid_items.id"), nullable=False)
    account_id = Column(String, nullable=False)  # Plaid account ID
    name = Column(String, nullable=False)
    official_name = Column(String)
    type = Column(String, nullable=False)  # e.g., "depository", "credit"
    subtype = Column(String)  # e.g., "checking", "savings"
    mask = Column(String)  # Last 4 digits
    balance_current = Column(Numeric(15, 2))
    balance_available = Column(Numeric(15, 2))
    currency_code = Column(String, default="USD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="accounts")
    plaid_item = relationship("PlaidItem", back_populates="accounts")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    plaid_transaction_id = Column(String, unique=True, nullable=True, index=True)

    amount = Column(Numeric(15, 2), nullable=False)
    date = Column(Date, nullable=False)
    name = Column(String, nullable=False)
    merchant_name = Column(String)
    category = Column(ARRAY(Text))
    primary_category = Column(Text)
    pending = Column(Boolean, default=False)
    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    account = relationship("Account")


class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # alert, warning, info, success, tip
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    action = Column(Text)
    amount = Column(Numeric(15, 2))
    category = Column(Text)
    priority = Column(Integer, default=5)
    dismissed = Column(Boolean, default=False)
    viewed = Column(Boolean, default=False)
    data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))

    user = relationship("User")


class BudgetPeriod(enum.Enum):
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    YEARLY = "yearly"


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String, nullable=False)  # e.g., "FOOD_AND_DRINK", "TRAVEL", etc.
    amount = Column(Numeric(15, 2), nullable=False)
    period = Column(String(20), nullable=False, default="monthly")
    is_active = Column(Boolean, default=True)
    alert_threshold = Column(Numeric(5, 2), default=80.0)  # Alert when spending reaches % of budget
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="budgets")

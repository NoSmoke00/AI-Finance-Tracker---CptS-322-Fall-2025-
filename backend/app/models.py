from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

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


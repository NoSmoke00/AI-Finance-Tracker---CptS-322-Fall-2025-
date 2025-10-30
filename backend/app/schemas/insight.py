from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime


class InsightBase(BaseModel):
    type: str
    title: str
    description: str
    action: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    priority: int = 5
    dismissed: bool = False
    viewed: bool = False
    data: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class InsightCreate(InsightBase):
    user_id: int


class InsightResponse(InsightBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True



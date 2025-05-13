from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from enum import Enum

# Write
class OrderStatus(str, Enum):
    pending = "pending"
    in_preparation = "in_preparation"
    ready = "ready"
    delivered = "delivered"
    failed = "failed"

class KitchenOrderMealCreate(BaseModel):
    meal_id: int
    meal_name: str
    recipe: str
    notes: Optional[str] = None
    quantity: int = Field(default=1, ge=1)

class KitchenOrderCreate(BaseModel):
    subscription_id: int
    user_id: int
    delivery_date: date
    delivery_address: str
    status: OrderStatus = OrderStatus.pending
    meals: List[KitchenOrderMealCreate]


# Read
class KitchenOrderMealRead(BaseModel):
    id: int
    meal_id: int
    meal_name: str
    meal_code: str
    tags: Optional[str]
    notes: Optional[str]
    quantity: int

    class Config:
        orm_mode = True

class KitchenOrderRead(BaseModel):
    id: int
    subscription_id: int
    user_id: int
    delivery_date: date
    delivery_address: str
    status: OrderStatus
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    meals: List[KitchenOrderMealRead]

    class Config:
        orm_mode = True

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from enum import Enum

class DeliveryOrderStatus(str, Enum):
    waiting_for_delivery = "waiting_for_delivery"
    in_progress = "in_progress"
    delivered = "delivered"
    failed = "failed"

class DeliveryOrderRead(BaseModel):
    id: int
    user_id: str
    kitchen_order_id: int
    delivery_date: date
    delivery_address: str
    status: DeliveryOrderStatus

    class Config:
        orm_mode = True

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


class WarehouseAddress(BaseModel):
    company_name: Optional[str]
    name: str
    phone: str
    email: str
    address_line1: str
    address_line2: Optional[str]
    city_locality: str
    state_province: str
    postal_code: str
    country_code: str
    address_residential_indicator: str = Field(..., regex="^(yes|no)$")

class WarehouseRequest(BaseModel):
    name: str
    origin_address: WarehouseAddress
    return_address: WarehouseAddress


class Address(BaseModel):
    name: str
    phone: str
    email: str
    address_line1: str
    address_line2: str = None
    city_locality: str
    state_province: str
    postal_code: str
    country_code: str = "US"
    address_residential_indicator: str = "yes"


class ShipmentRequest(BaseModel):
    ship_to: Address
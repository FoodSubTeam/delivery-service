from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import DeliveryOrder
from app.schemas import DeliveryOrderRead
from app.database import SessionLocal
from typing import List
from app.kafka import KafkaProducerSingleton
import json
import logging

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session


# Get delivery order by id
@router.get("/delivery-order/{order_id}", response_model=DeliveryOrderRead)
async def get_delivery_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DeliveryOrder)
        .where(DeliveryOrder.id == order_id)
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


# Get all delivery orders by delivery_id
@router.get("/delivery-orders/by-delivery/{delivery_id}", response_model=List[DeliveryOrderRead])
async def get_delivery_orders_by_delivery_id(
    delivery_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DeliveryOrder)
        .where(DeliveryOrder.delivery_id == delivery_id)
    )
    orders = result.scalars().all()

    if not orders:
        raise HTTPException(status_code=404, detail="No delivery orders found for this delivery")

    return orders


# Get all delivery orders
@router.get("/delivery-orders", response_model=List[DeliveryOrderRead])
async def list_delivery_orders(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DeliveryOrder)
    )
    orders = result.scalars().all()
    return orders


# Test kafka communication
@router.get("/delivery/test-kafka")
async def test_kafka():
    logging.warning("test_kafka called")
    test_msg = {
        "type": "generate_daily_delivery_orders",
        "data": {
            "date": "2025-05-05",
            "subscriptions": [
                {
                    "subscription_id": 1,
                    "user_id": 123,
                    "delivery_id": 1,
                    "delivery_address": "123 Food Street",
                    "meals": [
                        {"meal_id": 1, "meal_code": "MLE_001", "meal_name": "Pasta", "recipe": "Cook 10 min", "quantity": 2},
                        {"meal_id": 2, "meal_code": "MLE_002", "meal_name": "Salad", "recipe": "Cut tomato", "quantity": 1}
                    ]
                }
            ]
        }
    }
    KafkaProducerSingleton.produce_message("delivery.order", json.dumps(test_msg))
    logging.warning(f"Sent message: {json.dumps(test_msg)}")
    
    return {"message": "Ll!"}


# Test endpoint
@router.get("/delivery/test")
async def test_delivery():
    logging.warning("delivery test hit")
    return {"message": "ok"}

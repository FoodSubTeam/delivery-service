from fastapi import APIRouter, Depends, HTTPException, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import DeliveryOrder
from app.schemas import DeliveryOrderRead, WarehouseRequest
from app.database import SessionLocal
from typing import List, Optional
from app.kafka import KafkaProducerSingleton
from app.service import DeliveryService
import json
import logging

router = APIRouter()
service = DeliveryService()

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


# Add a warehouse
@router.post("/warehouse")
async def create_warehouse(
    warehouse: WarehouseRequest,
    db: AsyncSession = Depends(get_db)
):
    warehouse_id = service.handle_create_warehouse(warehouse, db)

    return {
        "message": "Warehouse created successfully",
        "warehouse_id": warehouse_id
    }


# Test endpoint
@router.get("/delivery/test")
async def test_delivery():
    logging.warning("delivery test hit")
    return {"message": "ok"}

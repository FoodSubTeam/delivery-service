from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import KitchenOrder, KitchenOrderMeal
from app.schemas import KitchenOrderCreate, KitchenOrderRead
from app.database import SessionLocal
from typing import List

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/kitchen/kitchen-orders/", response_model=KitchenOrderRead, status_code=201)
async def create_kitchen_order(
    order_in: KitchenOrderCreate,
    db: AsyncSession = Depends(get_db)
):
    order = KitchenOrder(
        subscription_id=order_in.subscription_id,
        user_id=order_in.user_id,
        delivery_date=order_in.delivery_date,
        delivery_address=order_in.delivery_address,
        status=order_in.status,
    )

    for meal_data in order_in.meals:
        meal = KitchenOrderMeal(
            meal_id=meal_data.meal_id,
            meal_name=meal_data.meal_name,
            meal_code=meal_data.meal_code,
            tags=meal_data.tags,
            notes=meal_data.notes,
            quantity=meal_data.quantity,
        )
        order.meals.append(meal)

    db.add(order)
    await db.commit()
    await db.refresh(order)

    await db.refresh(order, attribute_names=["meals"])

    return order

@router.get("/kitchen/kitchen-orders/{order_id}", response_model=KitchenOrderRead)
async def get_kitchen_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(KitchenOrder)
        .where(KitchenOrder.id == order_id)
        .options(selectinload(KitchenOrder.meals))
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

@router.get("/kitchen/kitchen-orders/", response_model=List[KitchenOrderRead])
async def list_kitchen_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(KitchenOrder)
        .options(selectinload(KitchenOrder.meals))
        .order_by(KitchenOrder.delivery_date.asc())
        .offset(skip)
        .limit(limit)
    )
    orders = result.scalars().all()
    return orders

@router.get("/kitchen/test")
async def test_kitchen():
    import logging
    logging.warning("kitchen test hit")
    return {"message": "ok"}

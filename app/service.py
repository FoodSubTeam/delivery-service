from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.models import DeliveryOrder, DeliveryOrderMeal
from datetime import datetime
import uuid
import logging

class DeliveryService():
    
    async def generate_delivery_orders_for_date(self, data: dict, db: AsyncSession):
        if not isinstance(data, list):
            raise ValueError("Expected input 'data' to be a list of offers")

        for offer in data:
            meals = offer.get("meals", [])
            order_data = DeliveryOrder(
                subscription_id=offer.get("subscription_id"),
                user_id=offer.get("user_id"),
                delivery_id=offer.get("delivery_id"),
                delivery_date=datetime.utcnow().date(),
                delivery_address=offer.get("delivery_address"),
                meals=[
                    DeliveryOrderMeal(
                        meal_id=meal["id"],
                        meal_code=meal["meal_code"],
                        meal_name=meal["name"],
                        description=meal["description"],
                        notes=meal.get("notes", ""),
                        quantity=meal["quantity"]
                    )
                    for meal in meals
                ]
            )

            db.add(order_data)
            await db.commit()
            await db.refresh(order_data)
            await db.refresh(order_data, attribute_names=["meals"])

        logging.warning(f"Created {len(data)} delivery orders.")
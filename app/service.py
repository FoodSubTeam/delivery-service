from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.models import KitchenOrder, KitchenOrderMeal
from datetime import datetime
import uuid
import logging

class KitchenService():
    
    async def generate_kitchen_orders_for_date(self, data: dict, db: AsyncSession):
        if not isinstance(data, list):
            raise ValueError("Expected input 'data' to be a list of offers")

        for offer in data:
            meals = offer.get("meals", [])
            order_data = KitchenOrder(
                subscription_id=offer.get("subscription_id"),
                user_id=offer.get("user_id"),
                kitchen_id=offer.get("kitchen_id"),
                delivery_date=datetime.utcnow().date(),
                delivery_address=offer.get("delivery_address"),
                meals=[
                    KitchenOrderMeal(
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

        logging.warning(f"Created {len(data)} kitchen orders.")
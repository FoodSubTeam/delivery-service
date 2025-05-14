from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.models import KitchenOrder, KitchenOrderMeal
from datetime import datetime
import uuid
import logging

class KitchenService():
    
    async def generate_kitchen_orders_for_date(self, data: dict, db: AsyncSession):
        subscriptions = data.get("subscriptions", [])
        if not isinstance(subscriptions, list):
            raise ValueError("Expected 'subscriptions' to be a list")
        
        date_str = data.get("date")
        delivery_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        for subscription in subscriptions:
            meals = subscription.get("meals", [])
            order_data = KitchenOrder(
                subscription_id=subscription.get("subscription_id"),
                user_id=subscription.get("user_id"),
                delivery_date=delivery_date,
                delivery_address=subscription.get("delivery_address"),
                meals=[
                    KitchenOrderMeal(
                        meal_id=meal["meal_id"],
                        meal_name=meal["meal_name"],
                        recipe=meal["recipe"],
                        notes=meal.get("notes", ""),  # default if missing
                        quantity=meal["quantity"]
                    )
                    for meal in meals
                ]
            )

            db.add(order_data)
            await db.commit()
            await db.refresh(order_data)
            await db.refresh(order_data, attribute_names=["meals"])

        logging.warning(f"Created {len(subscriptions)} kitchen orders.")

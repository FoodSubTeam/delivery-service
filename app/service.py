from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.models import KitchenOrder, KitchenOrderMeal
from datetime import datetime
import uuid

class KitchenService():
    
    async def generate_kitchen_orders_for_date(self, data: dict, db: AsyncSession):
        for subscription in data["subscriptions"]:
            order_data = KitchenOrder(
                subscription_id=subscription["subscription_id"],
                user_id=subscription["user_id"],
                delivery_date=data["date"],
                delivery_address=subscription["delivery_address"],
                meals=[
                    {
                        "meal_id": meal["meal_id"],
                        "meal_name": meal["meal_name"],
                        "recipe": meal["recipe"],
                        "notes": meal["notes"],
                        "quantity": meal["quantity"]
                    }
                    for meal in subscription["meals"]
                ]
            )

            db.add(order_data)
            await db.commit()
            await db.refresh(order_data)

            await db.refresh(order_data, attribute_names=["meals"])

        print(f"Created {len(subscription)} kitchen orders.")

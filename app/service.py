from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.models import DeliveryOrder
from datetime import datetime
import uuid
import logging

class DeliveryService():
    
    async def generate_delivery_orders_for_date(self, data: dict, db: AsyncSession):
        if not isinstance(data, list):
            raise ValueError("Expected input 'data' to be a list of order")

        for order in data:
            order_data = DeliveryOrder(
                user_id=order.get("user_id"),
                kitchen_order_id=order.get("id"),
                delivery_date=order.get("delivery_date"),
                delivery_address=order.get("delivery_address")
            )

            db.add(order_data)
            await db.commit()
            await db.refresh(order_data)

        logging.warning(f"Created {len(data)} delivery orders.")
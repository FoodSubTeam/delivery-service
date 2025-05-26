from app.service import KitchenService
from app.database import get_db
from app.topics import Topic, MessageType
import logging

service = KitchenService()

async def handle_generate_daily_orders(data):
    logging.warning(f"Received handle_generate_daily_orders message, data: {data}")
    async with get_db() as db:
        await service.generate_kitchen_orders_for_date(data, db)


handlers = {
    MessageType.GENERATE_KITCHEN_ORDERS.value: handle_generate_daily_orders,
}
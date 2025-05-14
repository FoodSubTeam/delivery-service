from app.service import KitchenService
from app.database import get_db
import logging

service = KitchenService()

async def handle_generate_daily_orders(data):
    date = data.get("date")
    logging.warning(f"Generating kitchen orders for {date}")    
    async with get_db() as db:
        await service.generate_kitchen_orders_for_date(data, db)


handlers = {
    "generate_daily_kitchen_orders": handle_generate_daily_orders,
}
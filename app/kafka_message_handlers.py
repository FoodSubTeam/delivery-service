from app.service import DeliveryService
from app.database import get_db
from app.topics import Topic, MessageType
from app.schemas import Address
import logging

service = DeliveryService()

async def handle_generate_delivery_orders(data):
    logging.warning(f"Received handle_generate_delivery_orders message, data: {data}")
    async with get_db() as db:
        customers_addresses = [Address(**item.get("user", {})) for item in data.get("data", [])]
        created_order_ids = await service.generate_delivery_orders_for_date(data, db)
        batch_id = await service.create_shipments(customers_addresses)
        service.update_orders_batch_id(created_order_ids, batch_id, db)


handlers = {
    MessageType.GENERATE_DELIVERY_ORDERS.value: handle_generate_delivery_orders,
}
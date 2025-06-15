from app.service import DeliveryService
from app.database import get_db
from app.topics import Topic, MessageType
from app.schemas import Address
import logging

service = DeliveryService()

async def handle_generate_delivery_orders(data):
    logging.warning(f"Received handle_generate_delivery_orders message, data: {data}")
    async with get_db() as db:
        address_json = {
            "name": "John Doe",
            "phone": "+1-555-123-4567",
            "email": "john.doe@example.com",
            "address_line1": "123 Main St",
            "address_line2": "Apt 4B",
            "city_locality": "Springfield",
            "state_province": "IL",
            "postal_code": "62704",
            "country_code": "US",
            "address_residential_indicator": "yes"
        }
        address_obj = Address(**address_json)

        # customers_addresses = [Address(**item.get("user", {})) for item in data.get("data", [])]
        customers_addresses = [address_obj]
        created_order_ids = await service.generate_delivery_orders_for_date(data, db)
        warehouse = await service.get_warehouse_id(db)
        warehouse_id = warehouse.id
        logging.warning(f"Got warehouse id: {warehouse_id}")
        batch_id = await service.create_shipments(customers_addresses, warehouse_id)
        await service.update_orders_batch_id(created_order_ids, batch_id, db)


handlers = {
    MessageType.GENERATE_DELIVERY_ORDERS.value: handle_generate_delivery_orders,
}
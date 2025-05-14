import time
import json
import asyncio
from app.kafka import KafkaConsumerSingleton
from app.service import KitchenService
from app.database import get_db

service = KitchenService()
    
async def handle_generate_daily_orders(data):
    date_str = data.get("date")
    if not date_str:
        print("Missing 'date' in message data")
        return

    print(f"Generating kitchen orders for {date_str}")
    
    async with get_db() as db:
        await service.generate_kitchen_orders_for_date(date_str, db)


handlers = {
    "generate_daily_kitchen_orders": handle_generate_daily_orders,
}


async def on_message_received(message_str):
    try:
        message = json.loads(message_str)
    except Exception as e:
        print(f"Failed to parse JSON message: {e}")
        return
    
    msg_type = message.get("type")
    data = message.get("data")

    if not msg_type:
        print("Error: message missing 'type'")
        return

    if msg_type in handlers:
        asyncio.create_task(handlers[msg_type](data))
    else:
        print(f"Unknown message type: {msg_type}")


def blocking_consume_loop():
    topics = ['kitchen.order']
    while True:
        message = KafkaConsumerSingleton.consume_message(topics)
        if message:
            # Schedule the async callback from the thread
            asyncio.run_coroutine_threadsafe(
                on_message_received(message),
                asyncio.get_event_loop()
            )
        time.sleep(1)


async def start_consumer():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, blocking_consume_loop)


# Messages:
# { "type": "generate_daily_kitchen_orders", "data": { "date": "2025-05-05" } }
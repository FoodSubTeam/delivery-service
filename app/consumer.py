from aiokafka import AIOKafkaConsumer
import asyncio
import json
from app.kafka_message_handlers import handlers
import logging

consumer = None

kafka_bootstrap_servers = 'kafka-service.kafka.svc.cluster.local:9092'

async def start_consumer():
    global consumer
    consumer = AIOKafkaConsumer(
        'kitchen.order',
        bootstrap_servers=kafka_bootstrap_servers,
        group_id="kitchen-group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            await handle_message(msg.value)
    finally:
        await consumer.stop()


async def handle_message(raw_message: bytes):
    try:
        message = json.loads(raw_message.decode())
        logging.warning(f"Message decoded once: {message}")
    except Exception as e:
        logging.warning(f"Failed to parse message: {e}")
        return

    msg_type = message.get("type")
    data = message.get("data")
    
    if isinstance(data, str):
        data = json.loads(data)

    if not msg_type:
        print("Missing message type")
        return

    handler = handlers.get(msg_type)
    if handler:
        asyncio.create_task(handler(data))  # Schedule the handler
    else:
        print(f"Unknown message type: {msg_type}")


# Messages:
# { "type": "generate_daily_kitchen_orders", "data": { "date": "2025-05-05" } }
from fastapi import FastAPI
from app.routes import router
from app.database import engine
from app.models import Base
from app.consumer import start_consumer
from app.kafka import init_topics
import logging
import asyncio
from sqlalchemy import inspect, text

app = FastAPI()

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Delivery Service is running"}

@app.on_event("startup")
async def on_startup():
    logging.getLogger("aiokafka").setLevel(logging.WARNING)
    # logging.basicConfig(level=logging.DEBUG)

    # Create tables on startup
    async with engine.begin() as conn:
        # await conn.execute(text("DROP TYPE orderstatus CASCADE"))
        # await conn.execute(text("DROP TABLE delivery_orders CASCADE"))
        # await conn.run_sync(Base.metadata.drop_all)  # Uncomment to reset database entries
        await conn.run_sync(Base.metadata.create_all)

    # Initialize all required topics for the service
    init_topics()

    # Consume messages from all subscribed topics
    asyncio.create_task(start_consumer())



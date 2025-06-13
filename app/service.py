from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select, delete, update
from sqlalchemy.orm import joinedload
from app.models import DeliveryOrder, Warehouse
from datetime import datetime
from app.schemas import Address, WarehouseRequest
from typing import List
from datetime import datetime
import logging
import httpx
import os
from fastapi import HTTPException
import copy

class DeliveryService():
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.getenv("SHIPENGINE_API_KEY")
        self.carrier_id = os.getenv("SHIPENGINE_CARRIER_ID")
        self.api_url = "https://api.shipengine.com/v1"
    

    async def generate_delivery_orders_for_date(self, data: dict, db: AsyncSession):
        if not isinstance(data, list):
            raise ValueError("Expected input 'data' to be a list of order")
        
        created_order_ids = []

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

            created_order_ids.append(order_data.id)

        logging.warning(f"Created {len(data)} delivery orders.")

        return created_order_ids

    
    async def update_orders_batch_id(self, order_ids, batch_id, db: AsyncSession):
        stmt = (
            update(DeliveryOrder)
            .where(DeliveryOrder.id.in_(order_ids))
            .values(batch_id=batch_id)
        )
        
        await db.execute(stmt)
        await db.commit()

    
    async def create_shipments(self, customers: List[Address]):
        headers = {
            "API-Key": self.secret_key,
            "Content-Type": "application/json"
        }

        payload = {
            "shipments": self.create_shipment_payload(customers)
        }

        async with httpx.AsyncClient() as client:
            try:
                # Create shipments
                shipment_res = await client.post(
                    f"{self.api_url}/shipments",
                    headers=headers,
                    json=payload
                )
                shipment_res.raise_for_status()
                shipment_data = shipment_res.json()
                shipment_ids = [shipment["shipment_id"] for shipment in shipment_data.get("shipments", [])]

                today = datetime.now().date()
                batches_payload = {
                    "batch_notes": f"Food delivery {today}",
                    "shipment_ids": shipment_ids
                }

                # Create a batch
                batch_res = await client.post(
                    f"{self.api_url}/batches",
                    headers=headers,
                    json=batches_payload
                )
                batch_res.raise_for_status()
                batch_data = batch_res.json()
                batch_id = batch_data.get("batch_id")

                now = datetime.now()
                process_batch_payload = {
                    "ship_date": f"{now}",
                    "label_layout": "4x6",
                    "label_format": "pdf"
                }

                # Process batch
                process_batch_res = await client.post(
                    f"{self.api_url}/batches/{batch_id}/process/labels",
                    headers=headers,
                    json=process_batch_payload
                )
                process_batch_res.raise_for_status()
                
                return batch_id

            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        

    def create_shipment_payload(self, customers: List[Address]):
        warehouse_id = self.get_warehouse_id().id

        base_shipment = {
            "validate_address": "no_validation",
            "service_code": "usps_priority_mail",
            "warehouse_id": warehouse_id,
            "confirmation": "none",
            "advanced_options": {},
            "insurance_provider": "none",
            "tags": [],
            "packages": [
                {
                    "weight": {
                        "value": 1.0,
                        "unit": "ounce"
                    }
                }
            ]
        }

        shipments_data = []

        for idx, customer in enumerate(customers):
            shipment = copy.deepcopy(base_shipment)

            shipment["external_shipment_id"] = f"order-{idx+1}"
            shipment["ship_to"] = {
                "name": customer.name,
                "phone": customer.phone,
                "email": customer.email,
                "address_line1": customer.address_line1,
                "city_locality": customer.city_locality,
                "state_province": customer.state_province,
                "postal_code": customer.postal_code,
                "country_code": customer.country_code,
                "address_residential_indicator": customer.address_residential_indicator
            }

            shipments_data.append(shipment)
        
        return shipments_data
        

    async def create_warehouse_request(self, warehouse: WarehouseRequest):
        headers = {
            "API-Key": self.secret_key,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                result = await client.post(
                    f"{self.api_url}/warehouses",
                    headers=headers,
                    json=warehouse.dict()
                )
                result.raise_for_status()
                data = result.json()
                warehouse_id = data["warehouse_id"]

                return warehouse_id

            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            
    
    async def handle_create_warehouse(self, warehouse: WarehouseRequest, db: AsyncSession):
        # Save warehouse id to db
        try:
            # Delete all warehouses
            await db.execute(delete(Warehouse))
            await db.commit()

            warehouse_id = await self.create_warehouse_request(warehouse)
            new_warehouse = Warehouse(id=warehouse_id)

            logging.warning(f"warehouse id created: {warehouse_id}")
            
            db.add(new_warehouse)
            await db.commit()
            await db.refresh(new_warehouse)

            return warehouse_id

        finally:
            db.close()


    async def get_warehouse_id(self, db: AsyncSession):
        result = await db.execute(
            select(Warehouse)
        )
        return result.scalars().first()
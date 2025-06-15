from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class DeliveryOrderStatus(enum.Enum):
    waiting_for_delivery = "waiting_for_delivery"
    in_progress = "in_progress"
    delivered = "delivered"
    failed = "failed"


class DeliveryOrder(Base):
    __tablename__ = 'delivery_orders'

    id = Column(Integer, primary_key=True)
    
    user_id = Column(String, nullable=False)
    kitchen_order_id = Column(Integer, nullable=False)
    delivery_date = Column(String, nullable=False)       
    status = Column(Enum(DeliveryOrderStatus), default=DeliveryOrderStatus.waiting_for_delivery, nullable=False)
    delivery_address = Column(String, nullable=False)
    batch_id = Column(String)

    def __repr__(self):
        return f"<DeliveryOrder id={self.id} date={self.delivery_date} status={self.status}>"


class Warehouse(Base):
    __tablename__ = 'warehouse'

    id = Column(String, primary_key=True)

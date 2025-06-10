from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class OrderStatus(enum.Enum):
    pending = "pending"
    in_preparation = "in_preparation"
    ready = "ready"
    delivered = "delivered"
    failed = "failed"

class DeliveryOrder(Base):
    __tablename__ = 'delivery_orders'

    id = Column(Integer, primary_key=True)
    
    subscription_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    delivery_id = Column(Integer, nullable=False)
    delivery_date = Column(Date, nullable=False)       
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    delivery_address = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    meals = relationship("DeliveryOrderMeal", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DeliveryOrder id={self.id} date={self.delivery_date} status={self.status}>"

class DeliveryOrderMeal(Base):
    __tablename__ = 'delivery_order_meals'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('delivery_orders.id'), nullable=False)
    
    meal_id = Column(Integer, nullable=False)
    meal_code = Column(String, nullable=False)
    meal_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    notes = Column(String)
    quantity = Column(Integer, default=1, nullable=False)

    order = relationship("DeliveryOrder", back_populates="meals")

    def __repr__(self):
        return f"<DeliveryOrderMeal id={self.id} name={self.meal_name} qty={self.quantity}>"

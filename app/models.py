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

class KitchenOrder(Base):
    __tablename__ = 'kitchen_orders'

    id = Column(Integer, primary_key=True)
    
    subscription_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    delivery_date = Column(Date, nullable=False)       
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    delivery_address = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    meals = relationship("KitchenOrderMeal", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<KitchenOrder id={self.id} date={self.delivery_date} status={self.status}>"

class KitchenOrderMeal(Base):
    __tablename__ = 'kitchen_order_meals'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('kitchen_orders.id'), nullable=False)
    
    meal_id = Column(Integer, nullable=False)
    meal_name = Column(String, nullable=False)
    recipe = Column(String, nullable=False)
    notes = Column(String)
    quantity = Column(Integer, default=1, nullable=False)

    order = relationship("KitchenOrder", back_populates="meals")

    def __repr__(self):
        return f"<KitchenOrderMeal id={self.id} name={self.meal_name} qty={self.quantity}>"

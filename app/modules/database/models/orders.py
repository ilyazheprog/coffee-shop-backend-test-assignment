from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from modules.database.core import Base
from datetime import datetime


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    delivery_method_id = Column(Integer, ForeignKey("delivery_methods.id"), nullable=False)
    total_price = Column(Float, nullable=False)
    status_id = Column(Integer, ForeignKey("order_statuses.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    delivery_method = relationship("DeliveryMethod")
    status = relationship("OrderStatus")

    menu_items = relationship(
        "MenuItem", secondary="order_menu_items", back_populates="orders"
    )
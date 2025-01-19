from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from modules.database.core import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)  # Идентификатор пользователя
    delivery_method_id = Column(
        Integer, ForeignKey("delivery_methods.id"), nullable=False
    )  # Способ доставки
    total_price = Column(Float, nullable=False)  # Общая стоимость заказа
    status_id = Column(
        Integer, ForeignKey("order_statuses.id"), nullable=False
    )  # Статус заказа

    delivery_method = relationship("DeliveryMethod")  # Связь со способом доставки
    status = relationship("OrderStatus")  # Связь со статусом заказа

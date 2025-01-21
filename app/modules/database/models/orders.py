from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from modules.database.core import Base


class OrderMenuItem(Base):
    __tablename__ = "order_menu_items"

    order_id = Column(
        Integer, ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True
    )
    menu_item_id = Column(
        Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), primary_key=True
    )
    quantity = Column(Integer, nullable=False)

    # Указываем `overlaps` для предотвращения конфликтов
    order = relationship(
        "Order", back_populates="order_menu_items", overlaps="menu_items"
    )
    menu_item = relationship(
        "MenuItem", back_populates="order_menu_items", overlaps="orders"
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    delivery_method_id = Column(
        Integer, ForeignKey("delivery_methods.id"), nullable=False
    )
    total_price = Column(Float, nullable=False)
    status_id = Column(Integer, ForeignKey("order_statuses.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    delivery_method = relationship("DeliveryMethod")
    status = relationship("OrderStatus")

    # Указываем `overlaps` для предотвращения конфликтов
    menu_items = relationship(
        "MenuItem",
        secondary="order_menu_items",
        back_populates="orders",
        overlaps="order_menu_items",
    )
    order_menu_items = relationship(
        "OrderMenuItem",
        back_populates="order",
        cascade="all, delete-orphan",
        overlaps="menu_items",
    )


class MenuCategory(Base):
    __tablename__ = "menu_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    menu_items = relationship(
        "MenuItem", back_populates="category", cascade="all, delete-orphan"
    )


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category_id = Column(
        Integer, ForeignKey("menu_categories.id", ondelete="CASCADE"), nullable=False
    )
    weight = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    category = relationship("MenuCategory", back_populates="menu_items")
    orders = relationship(
        "Order",
        secondary="order_menu_items",
        back_populates="menu_items",
        overlaps="order_menu_items",
    )
    order_menu_items = relationship(
        "OrderMenuItem",
        back_populates="menu_item",
        cascade="all, delete-orphan",
        overlaps="orders",
    )

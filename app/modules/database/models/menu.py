from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from modules.database.core import Base

class MenuCategory(Base):
    __tablename__ = "menu_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    menu_items = relationship("MenuItem", back_populates="category", cascade="all, delete-orphan")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("menu_categories.id", ondelete="CASCADE"), nullable=False)
    weight = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    category = relationship("MenuCategory", back_populates="menu_items")
    orders = relationship(
        "Order", secondary="order_menu_items", back_populates="menu_items"
    )
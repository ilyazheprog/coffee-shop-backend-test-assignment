from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from modules.database.core import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Float, nullable=False)

    product = relationship("Product")
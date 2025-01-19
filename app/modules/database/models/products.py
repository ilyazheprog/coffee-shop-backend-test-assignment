from sqlalchemy import Column, Integer, String, Float, Boolean
from modules.database.core import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    price = Column(Float, nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)

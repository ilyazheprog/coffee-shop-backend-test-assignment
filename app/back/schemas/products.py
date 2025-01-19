from pydantic import BaseModel
from typing import Optional
from .out import ORMSchema


class ProductCreate(BaseModel):
    name: str
    price: float
    in_stock: bool = True  # Наличие по умолчанию


class ProductOut(ORMSchema):
    id: int
    name: str
    price: float
    in_stock: bool


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None

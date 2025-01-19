from pydantic import BaseModel
from typing import List
from .out import ORMSchema


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int


class CartItemOut(ORMSchema):
    id: int
    product_id: int
    quantity: int
    total_price: float


class CartOut(ORMSchema):
    items: List[CartItemOut]

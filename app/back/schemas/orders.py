from pydantic import BaseModel
from typing import Optional
from .out import ORMSchema


class OrderCreate(BaseModel):
    user_id: int
    delivery_method_id: int
    total_price: float
    status_id: int


class OrderOut(ORMSchema):
    id: int
    user_id: int
    delivery_method_id: int
    total_price: float
    status_id: int


class OrderUpdateStatus(BaseModel):
    status_id: int


class OrderUpdatePrice(BaseModel):
    total_price: float

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .out import ORMSchema


class MenuItemInOrder(BaseModel):
    menu_item_id: int
    quantity: int


class OrderCreate(BaseModel):
    user_id: int
    delivery_method_id: int
    status_id: int
    items: List[MenuItemInOrder]


class UserForOrder(BaseModel):
    user_id: int


class OrderOut(ORMSchema):
    id: int
    user_id: int
    delivery_method_id: int
    delivery_method_name: str
    total_price: float
    status_id: int
    status_name: str
    created_at: datetime
    items: Optional[List[MenuItemInOrder]]


class OrderUpdateStatus(BaseModel):
    status_id: int


class OrderUpdatePrice(BaseModel):
    total_price: float


class OrderMenuItemOut(BaseModel):
    id: int
    name: str
    price: float
    quantity: int

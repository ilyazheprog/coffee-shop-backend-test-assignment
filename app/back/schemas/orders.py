from pydantic import BaseModel
from typing import Optional, List
from .out import ORMSchema


class MenuItemInOrder(BaseModel):
    menu_item_id: int
    quantity: int


class OrderCreate(BaseModel):
    user_id: int
    delivery_method_id: int
    status_id: int
    items: List[MenuItemInOrder]


class OrderOut(ORMSchema):
    id: int
    user_id: int
    delivery_method_id: int
    total_price: float
    status_id: int
    menu_items: List[dict]


class OrderUpdateStatus(BaseModel):
    status_id: int


class OrderUpdatePrice(BaseModel):
    total_price: float


class OrderMenuItemOut(BaseModel):
    id: int
    name: str
    price: float
    quantity: int

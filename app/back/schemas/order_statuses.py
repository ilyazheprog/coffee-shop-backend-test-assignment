from pydantic import BaseModel, Field

from .out import ORMSchema


class OrderStatusBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)


class OrderStatusOut(OrderStatusBase, ORMSchema):
    id: int


class OrderStatusCreate(OrderStatusBase): ...


class OrderStatusUpdate(OrderStatusBase): ...

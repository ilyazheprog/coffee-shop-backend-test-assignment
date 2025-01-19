from pydantic import BaseModel
from .out import ORMSchema


class DeliveryMethodCreate(BaseModel):
    name: str


class DeliveryMethodOut(ORMSchema):
    id: int
    name: str

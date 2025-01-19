from .out import ORMSchema
from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    tg_id: int
    role_id: int
    username: Optional[str] = None


class UserOut(ORMSchema):
    id: int
    username: Optional[str]
    role_id: int


class RoleChange(BaseModel):
    new_role_id: int

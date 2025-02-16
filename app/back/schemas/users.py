from typing import Optional

from pydantic import BaseModel

from .out import ORMSchema


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

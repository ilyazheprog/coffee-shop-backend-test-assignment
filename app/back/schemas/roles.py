from pydantic import BaseModel, Field
from .out import ORMSchema


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)


class RoleOut(RoleBase, ORMSchema):
    id: int = Field(..., gt=0)


class RoleCreate(RoleOut): ...


class RoleUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)


__all__ = ["RoleOut", "RoleCreate", "RoleUpdate"]

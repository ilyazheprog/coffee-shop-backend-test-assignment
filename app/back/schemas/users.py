from typing import Optional
from pydantic import BaseModel, Field, PositiveInt


class UserBase(BaseModel):
    role_id: int = Field(..., ge=1, le=3)
    username: Optional[str] = Field(..., min_length=1, max_length=255)


class UserOut(UserBase):
    id: int = Field(..., gt=0)


class UserCreate(UserOut): ...


class UserUpdate(BaseModel):
    role_id: Optional[int] = Field(..., ge=1, le=3)
    username: Optional[str] = Field(..., min_length=1, max_length=255)

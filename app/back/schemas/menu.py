from pydantic import BaseModel

from .out import ORMSchema


class MenuCategoryBase(BaseModel):
    name: str


class MenuCategoryCreate(MenuCategoryBase):
    pass


class MenuCategoryOut(MenuCategoryBase, ORMSchema):
    id: int


class MenuItemBase(BaseModel):
    name: str
    category_id: int
    weight: float
    price: float
    is_available: bool


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemOut(MenuItemBase, ORMSchema):
    id: int

from fastapi import APIRouter
from api.roles import router as roles_r
from api.users import router as users_r
from api.products import router as products_r
from api.carts_item import router as ci_r
from api.orders import router as order_r
from api.delivery_methods import router as deliv_r

global_router = APIRouter()
global_router.include_router(roles_r)
global_router.include_router(users_r)
global_router.include_router(products_r)
global_router.include_router(ci_r)
global_router.include_router(deliv_r)
global_router.include_router(order_r)

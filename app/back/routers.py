from fastapi import APIRouter
from api.roles import router as roles_r
from api.users import router as users_r
from api.orders import router as order_r
from api.delivery_methods import router as deliv_r
from api.menu_items import router as mi_r
from api.menu_categories import router as mc_r

global_router = APIRouter()
global_router.include_router(roles_r)
global_router.include_router(users_r)
global_router.include_router(deliv_r)
global_router.include_router(order_r)
global_router.include_router(mi_r)
global_router.include_router(mc_r)
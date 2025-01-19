from fastapi import APIRouter
from api.roles import router as roles_r
from api.users import router as users_r

global_router = APIRouter()
global_router.include_router(roles_r)
global_router.include_router(users_r)
from aiogram import F, Router

from bot.filters import AdminFilter
from modules.dataclasses import Type

client_router = Router()
admin_router = Router()

client_router.message.filter(F.chat.type == Type.PRIVATE, ~AdminFilter())
admin_router.message.filter(F.chat.type == Type.PRIVATE, AdminFilter())

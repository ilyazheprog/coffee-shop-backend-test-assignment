from aiogram import F, Router

from bot.filters import AdminFilter, BaristaFilter, ChatTypeFilter

client_router = Router()
admin_router = Router()
barista_router = Router()

client_router.message.filter(
    ChatTypeFilter("private"), ~AdminFilter(), ~BaristaFilter()
)
barista_router.message.filter(ChatTypeFilter("private"), BaristaFilter())
admin_router.message.filter(ChatTypeFilter("private"), AdminFilter())

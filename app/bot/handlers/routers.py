from aiogram import F, Router
from bot.filters import AdminFilter, ChatTypeFilter

client_router = Router()
admin_router = Router()

client_router.message.filter(ChatTypeFilter("private"), ~AdminFilter())
admin_router.message.filter(ChatTypeFilter("private"), AdminFilter())

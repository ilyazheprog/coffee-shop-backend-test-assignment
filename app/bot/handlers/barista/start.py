from aiogram import Router, types
from aiogram.filters import CommandStart
import httpx

from bot.handlers.routers import barista_router
from bot.keyboards import barista_and_admin_main_menu_kb
from modules.envs import settings

router = Router()
barista_router.include_router(router)

BACKEND_URL = settings.bot.backend_url


@router.message(CommandStart())
async def start(message: types.Message):
    """Стартовое сообщение для баристы."""
    await message.reply(
        "Добро пожаловать в панель баристы!\n"
        "Доступные команды:\n"
        "/orders - Просмотр заказов\n"
        "/set_status <order_id> <new_status> - Обновить статус заказа\n"
        "/statuses - Список статусов заказов",
        reply_markup=barista_and_admin_main_menu_kb,
    )

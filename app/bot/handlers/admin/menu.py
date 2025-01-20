
from aiogram import Router, types
from aiogram.filters import Command
import httpx
from modules.envs.settings import settings
from bot.handlers.routers import admin_router

router = Router()
admin_router.include_router(router)

BACKEND_URL = settings.bot.backend_url

@router.message(Command("menu"))
async def admin_menu_commands(message: types.Message):
    """Просмотр и управление категориями и позициями меню."""
    await message.reply(
        "Управление меню:\n"
        "/menu_categories - Просмотр категорий меню\n"
        "/add_category <name> - Добавить категорию меню\n"
        "/menu_items - Просмотр позиций меню\n"
        "/add_menu_item <name> <category_id> <weight> <price> - Добавить позицию меню\n"
        "/remove_category <category_id> - Удалить категорию меню\n"
        "/remove_menu_item <item_id> - Удалить позицию меню"
    )

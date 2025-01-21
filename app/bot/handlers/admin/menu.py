from aiogram import Router, types
from aiogram.filters import Command

from bot.handlers.routers import admin_router
from bot.keyboards import barista_and_admin_main_menu_kb
from modules.envs.settings import settings

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
        "/set_menu_item_availability <item_id> <is_available (1|0)> - Изменить наличие позиции\n"
        "/add_menu_item <name> <category_id> <weight> <price> - Добавить позицию меню\n"
        "/remove_category <category_id> - Удалить категорию меню\n"
        "/remove_menu_item <item_id> - Удалить позицию меню",
        reply_markup=barista_and_admin_main_menu_kb,
    )

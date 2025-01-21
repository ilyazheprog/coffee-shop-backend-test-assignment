from aiogram import F, Router, types
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
import httpx

from bot.handlers.routers import client_router
from bot.keyboards import client_main_menu_kb
from bot.states import ClientStates
from modules.dataclasses import Buttons
from modules.dataclasses.roles import Role
from modules.envs import settings

router = Router()
client_router.include_router(router)

BACKEND_URL = settings.bot.backend_url


def get_name_by_id(data, target_id, cache={}):
    if target_id not in cache:
        cache.update({item["id"]: item["name"] for item in data})
    return cache.get(target_id)


@router.message(F.text == Buttons.MENU, ClientStates.main_menu)
async def view_menu(message: types.Message, state: FSMContext):
    """Просмотр меню."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/menu-items/?is_available=true")

        if response.status_code == 404:
            await message.reply("Меню пусто.")
            return

        menu = response.json()

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/menu-categories/")
        menu_categories = response.json()

    menu_list = "\n".join(
        f"Название: {item['name']}, "
        f"Категория: {get_name_by_id(menu_categories,item['category_id'])}, Вес: {item['weight']}, "
        f"Цена: {item['price']}"
        "\n================="
        for item in menu
    )
    await message.reply(f"Меню:\n{menu_list}")

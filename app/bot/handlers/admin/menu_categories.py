from aiogram import Router, types
from aiogram.filters import Command
import httpx

from bot.handlers.routers import admin_router
from modules.envs.settings import settings

router = Router()
admin_router.include_router(router)

BACKEND_URL = settings.bot.backend_url


@router.message(Command("menu_categories"))
async def list_menu_categories(message: types.Message):
    """
    Получает список всех категорий меню.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BACKEND_URL}/menu-categories/")
            response.raise_for_status()
            categories = response.json()

            if not categories:
                await message.reply("Категории меню отсутствуют.")
                return

            categories_list = "\n".join(
                f"ID: {cat['id']}, Название: {cat['name']}" for cat in categories
            )
            await message.reply(f"Список категорий меню:\n{categories_list}")
        except httpx.RequestError as e:
            await message.reply(f"Ошибка при запросе категорий меню: {str(e)}")
        except httpx.HTTPStatusError as e:
            await message.reply(f"Ошибка на сервере: {e.response.text}")


@router.message(Command("add_category"))
async def add_menu_category(message: types.Message):
    """
    Добавляет новую категорию меню.
    Используйте: /add_category <name>
    """
    try:
        _, name = message.text.split(maxsplit=1)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/menu-categories/",
                json={"name": name},
            )
            response.raise_for_status()

            if response.status_code == 201:
                await message.reply(f"Категория '{name}' успешно добавлена.")
            else:
                await message.reply(
                    f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}"
                )
    except ValueError:
        await message.reply(
            "Некорректный формат команды. Используйте: /add_category <name>"
        )
    except httpx.RequestError as e:
        await message.reply(f"Ошибка при добавлении категории: {str(e)}")
    except httpx.HTTPStatusError as e:
        await message.reply(f"Ошибка на сервере: {e.response.text}")

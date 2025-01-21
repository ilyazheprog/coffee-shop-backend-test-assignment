from aiogram import Router, types
from aiogram.filters import Command
import httpx

from bot.handlers.routers import admin_router
from modules.envs.settings import settings

router = Router()
admin_router.include_router(router)

BACKEND_URL = settings.bot.backend_url


@router.message(Command("menu_items"))
async def list_menu_items(message: types.Message):
    """
    Получает список всех позиций меню, включая названия категорий.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Получаем список позиций меню
            items_response = await client.get(f"{BACKEND_URL}/menu-items/")
            items_response.raise_for_status()
            items = items_response.json()

            if not items:
                await message.reply("Позиции меню отсутствуют.")
                return

            # Получаем список категорий
            categories_response = await client.get(f"{BACKEND_URL}/menu-categories/")
            categories_response.raise_for_status()
            categories = {cat["id"]: cat["name"] for cat in categories_response.json()}

            # Формируем список позиций с названием категории
            items_list = "\n".join(
                f"ID: {item['id']}, Название: {item['name']}, "
                f"Категория: {categories.get(item['category_id'], 'Неизвестно')}, "
                f"Вес: {item['weight']}г, Цена: {item['price']} руб."
                f"{'В' if item['is_available'] else 'Не в'} наличии"
                "\n==============="
                for item in items
            )
            await message.reply(f"Список позиций меню:\n{items_list}")
        except httpx.RequestError as e:
            await message.reply(f"Ошибка при запросе данных: {str(e)}")
        except httpx.HTTPStatusError as e:
            await message.reply(f"Ошибка на сервере: {e.response.text}")


@router.message(Command("add_menu_item"))
async def add_menu_item(message: types.Message):
    """
    Добавляет новую позицию в меню.
    Используйте: /add_menu_item <name> <category_id> <weight> <price>
    """
    try:
        _, name, category_id, weight, price = message.text.split(maxsplit=4)
        weight = float(weight)
        price = float(price)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/menu-items/",
                json={
                    "name": name,
                    "category_id": int(category_id),
                    "weight": weight,
                    "price": price,
                    "is_available": False,
                },
            )
            response.raise_for_status()

            if response.status_code == 201:
                await message.reply(f"Позиция '{name}' успешно добавлена в меню.")
            else:
                await message.reply(
                    f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}"
                )
    except ValueError:
        await message.reply(
            "Некорректный формат команды. Используйте: /add_menu_item <name> <category_id> <weight> <price>"
        )
    except httpx.RequestError as e:
        await message.reply(f"Ошибка при добавлении позиции: {str(e)}")
    except httpx.HTTPStatusError as e:
        await message.reply(f"Ошибка на сервере: {e.response.text}")


@router.message(Command("remove_menu_item"))
async def remove_menu_item(message: types.Message):
    """
    Удаляет позицию меню.
    Используйте: /remove_menu_item <item_id>
    """
    try:
        _, item_id = message.text.split(maxsplit=1)
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{BACKEND_URL}/menu-items/{item_id}/")
            response.raise_for_status()
            await message.reply(f"Позиция ID {item_id} успешно удалена.")
    except ValueError:
        await message.reply(
            "Некорректный формат команды. Используйте: /remove_menu_item <item_id>"
        )
    except httpx.RequestError as e:
        await message.reply(f"Ошибка при удалении позиции: {str(e)}")
    except httpx.HTTPStatusError as e:
        await message.reply(f"Ошибка на сервере: {e.response.text}")


@router.message(Command("set_menu_item_availability"))
async def set_menu_item_availability(message: types.Message):
    """
    Устанавливает доступность позиции меню.
    Используйте: /set_menu_item_availability <item_id> <is_available (1|0)>
    """
    try:
        _, item_id, is_available = message.text.split(maxsplit=2)
        is_available = "true" if is_available == "1" else "false"
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{BACKEND_URL}/menu-items/{item_id}/availability?is_available={is_available}",
            )
            response.raise_for_status()
            await message.reply(
                f"Доступность позиции ID {item_id} установлена на {is_available}."
            )
    except ValueError:
        await message.reply(
            "Некорректный формат команды. Используйте: /set_menu_item_availability <item_id> <is_available>"
        )
    except httpx.RequestError as e:
        await message.reply(f"Ошибка при установке доступности позиции: {str(e)}")
    except httpx.HTTPStatusError as e:
        await message.reply(f"Ошибка на сервере: {e.response.text}")

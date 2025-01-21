from aiogram import Router, types
from aiogram.filters import Command
import httpx

from bot.handlers.routers import admin_router
from modules.envs.settings import settings

router = Router()
admin_router.include_router(router)

BACKEND_URL = settings.bot.backend_url


@router.message(Command("delivery_methods"))
async def list_delivery_methods(message: types.Message):
    """Получает список способов доставки."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BACKEND_URL}/delivery-methods/")
            response.raise_for_status()
            delivery_methods = response.json()

            if not delivery_methods:
                await message.reply("Способы доставки отсутствуют.")
                return

            delivery_list = "\n".join(
                f"ID: {method['id']}, {method['name']}" for method in delivery_methods
            )
            await message.reply(f"Способы доставки:\n{delivery_list}")
        except httpx.RequestError as e:
            await message.reply(f"Ошибка при запросе способов доставки: {str(e)}")
        except httpx.HTTPStatusError as e:
            await message.reply(f"Ошибка на сервере: {e.response.text}")


@router.message(Command("add_delivery"))
async def add_delivery_method(message: types.Message):
    """
    Добавляет новый способ доставки.
    """
    try:
        _, name = message.text.split(maxsplit=1)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/delivery-methods/",
                json={"name": name},
            )
            response.raise_for_status()

            if response.status_code == 200:
                await message.reply(f"Способ доставки '{name}' успешно добавлен.")
            else:
                await message.reply(
                    f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}"
                )
    except ValueError:
        await message.reply(
            "Некорректный формат команды. Используйте: /add_delivery <name>"
        )
    except httpx.RequestError as e:
        await message.reply(f"Ошибка при добавлении способа доставки: {str(e)}")
    except httpx.HTTPStatusError as e:
        await message.reply(f"Ошибка на сервере: {e.response.text}")

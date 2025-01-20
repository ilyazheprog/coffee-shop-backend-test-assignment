from aiogram import Router, types
from aiogram.filters import Command
import httpx
from modules.envs.settings import settings
from bot.handlers.routers import admin_router

router = Router()
admin_router.include_router(router)

BACKEND_URL = settings.bot.backend_url

@router.message(Command("assign_barista"))
async def assign_barista_role(message: types.Message):
    """
    Назначает роль Бариста пользователю через бэкенд.
    """
    try:
        _, tg_id = message.text.split()
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{BACKEND_URL}/users/change-role/{tg_id}",
                json={"new_role_id": 2},  # ID роли "Бариста"
            )
            response.raise_for_status()

            if response.status_code == 200:
                await message.reply(f"Роль 'Бариста' успешно назначена пользователю с ID {tg_id}.")
            else:
                await message.reply(f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}")
    except ValueError:
        await message.reply("Некорректный формат команды. Используйте: /assign_barista <tg_id>")
    except httpx.RequestError as e:
        await message.reply(f"Ошибка при назначении роли: {str(e)}")
    except httpx.HTTPStatusError as e:
        await message.reply(f"Ошибка на сервере: {e.response.text}")



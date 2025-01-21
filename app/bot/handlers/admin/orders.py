from aiogram import Router, types
from aiogram.filters import Command
import httpx

from bot.handlers.routers import admin_router
from modules.envs.settings import settings

router = Router()
admin_router.include_router(router)

BACKEND_URL = settings.bot.backend_url


@router.message(Command("orders"))
async def list_orders(message: types.Message):
    """Получает список заказов с бэкенда."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BACKEND_URL}/orders/")
            response.raise_for_status()
            orders = response.json()

            if not orders:
                await message.reply("Нет активных заказов.")
                return

            order_list = "\n".join(
                f"ID: {order['id']}, Пользователь: {order['user_id']}, "
                f"Статус: {order['status']}, Сумма: {order['total_price']}"
                f"Дата создания: {order['created_at']}"
                for order in orders
            )
            await message.reply(f"Список заказов:\n{order_list}")
        except httpx.RequestError as e:
            await message.reply(f"Ошибка при запросе заказов: {str(e)}")
        except httpx.HTTPStatusError as e:
            await message.reply(f"Ошибка на сервере: {e.response.text}")

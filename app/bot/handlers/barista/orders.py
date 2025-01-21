from aiogram import Router, types
from aiogram.filters import Command
import httpx

from bot.handlers.routers import barista_router
from modules.envs.settings import settings

router = Router()
barista_router.include_router(router)

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

            res_text = ""
            for order in orders:
                order_id = order["id"]
                user_id = order["user_id"]
                delivery_method_name = order["delivery_method_name"]
                status_name = order["status_name"]
                total_price = order["total_price"]
                created_at = order["created_at"]
                menu_items = order["items"]

                res_text += f"Заказ №{order_id}\nID заказчика: {user_id}\nпособ доставки: {delivery_method_name}\nСтатус: {status_name}\nСумма: {total_price}\nДата: {created_at}\n"
                res_text += "Позиции:\n"

                for item in menu_items:
                    item_id = item["menu_item_id"]
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            f"{BACKEND_URL}/menu-items/{item_id}"
                        )
                        item_data = response.json()
                        item_name = item_data["name"]
                    res_text += f"{item_name} - {item['quantity']} шт.\n"

                res_text += "\n"
            await message.reply(f"Список заказов:\n{res_text}")
        except httpx.RequestError as e:
            await message.reply(f"Ошибка при запросе заказов: {str(e)}")
        except httpx.HTTPStatusError as e:
            await message.reply(f"Ошибка на сервере: {e.response.text}")

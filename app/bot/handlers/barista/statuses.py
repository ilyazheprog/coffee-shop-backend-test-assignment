from aiogram import Bot, Router, types
from aiogram.filters import Command
import httpx

from bot.handlers.routers import barista_router
from modules.dataclasses.order_status import OrderStatus
from modules.envs import settings

router = Router()
barista_router.include_router(router)
BACKEND_URL = settings.bot.backend_url


@router.message(Command("statuses"))
async def list_order_statuses(message: types.Message):
    """
    Отображает список всех статусов заказов.
    """
    statuses = [
        (OrderStatus.PENDING_ID, OrderStatus.PENDING_NAME),
        (OrderStatus.PROCESSING_ID, OrderStatus.PROCESSING_NAME),
        (OrderStatus.COMPLETED_ID, OrderStatus.COMPLETED_NAME),
    ]

    statuses_list = "\n".join(
        f"ID: {status_id}, Название: {status_name}"
        for status_id, status_name in statuses
    )
    await message.reply(f"Список статусов заказов:\n{statuses_list}")


@router.message(Command("set_status"))
async def set_order_status(message: types.Message, bot: Bot):
    """
    Устанавливает статус заказа.
    """
    try:
        order_id, new_status_id = map(int, message.text.split()[1:])
    except ValueError:
        await message.reply(
            "Неверный формат команды. Пример: /set_status <order_id> <new_status>"
        )
        return

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{BACKEND_URL}/orders/{order_id}/status",
                json={"status_id": new_status_id},
            )
            response.raise_for_status()
            await message.reply("Статус заказа обновлен.")
        except httpx.RequestError as e:
            await message.reply(f"Ошибка при обновлении статуса заказа: {str(e)}")
        except httpx.HTTPStatusError as e:
            await message.reply(f"Ошибка на сервере: {e.response.text}")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/orders/{order_id}/user")
        user_id = response.json()["user_id"]
    status = ""
    match new_status_id:
        case OrderStatus.PENDING_ID:
            status = OrderStatus.PENDING_NAME
        case OrderStatus.PROCESSING_ID:
            status = OrderStatus.PROCESSING_NAME
        case OrderStatus.COMPLETED_ID:
            status = OrderStatus.COMPLETED_NAME

    await bot.send_message(
        user_id, f"Статус вашего заказа №{order_id} был обновлен на '{status}'."
    )

from aiogram import Router, types
from aiogram.filters import Command
from modules.dataclasses.order_status import OrderStatus
from bot.handlers.routers import admin_router

router = Router()
admin_router.include_router(router)

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

    statuses_list = "\n".join(f"ID: {status_id}, Название: {status_name}" for status_id, status_name in statuses)
    await message.reply(f"Список статусов заказов:\n{statuses_list}")
from aiogram import Router, types
from aiogram.filters import CommandStart

from bot.handlers.routers import admin_router

router = Router()
admin_router.include_router(router)


@router.message(CommandStart())
async def admin_panel(message: types.Message):
    """Вход в административную панель."""
    await message.reply(
        "Добро пожаловать в административную панель!\n"
        "Доступные команды:\n"
        "/orders - Просмотр заказов\n"
        "/set_status <order_id> <new_status> - Обновить статус заказа\n"
        "/menu - Просмотр меню\n"
        "/product <product_id> - Просмотр информации о продукте\n"
        "/add_product <name> <price> <in_stock> - Добавить продукт\n"
        "/set_stock <product_id> <1|0> - Обновить наличие товара\n"
        "/assign_barista <tg_id> - Назначить роль Бариста\n"
        "/delivery_methods - Список способов доставки\n"
        "/add_delivery <name> - Добавить новый способ доставки\n"
        "/statuses - Список статусов заказов"
    )

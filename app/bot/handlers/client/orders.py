from aiogram import F, Router, types
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
import httpx

from bot.handlers.routers import client_router
from bot.keyboards.callback import (
    confirm_order_kb,
    generate_categories_keyboard,
    generate_delivery_methods_keyboard,
    generate_menu_keyboard,
    generate_quantity_keyboard,
)
from bot.states import ClientStates
from modules.dataclasses import Buttons, OrderStatus
from modules.dataclasses.roles import Role
from modules.envs import settings

router = Router()
client_router.include_router(router)

BACKEND_URL = settings.bot.backend_url


def get_name_by_id(data, target_id, key="menu_item_id", cache={}):
    if target_id not in cache:
        cache.update({item[key]: item["name"] for item in data})
    return cache.get(target_id)


@router.message(F.text == Buttons.ORDERS, ClientStates.main_menu)
async def view_orders(message: types.Message, state: FSMContext):
    """Просмотр заказов."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/orders/user/{message.from_user.id}")

        orders = response.json()
        if not orders:
            await message.reply("Нет заказов.")
            return

    res_text = ""
    for order in orders:
        order_id = order["id"]
        delivery_method_name = order["delivery_method_name"]
        status_name = order["status_name"]
        total_price = order["total_price"]
        created_at = order["created_at"]
        menu_items = order["items"]

        res_text += f"Заказ №{order_id}\nСпособ доставки: {delivery_method_name}\nСтатус: {status_name}\nСумма: {total_price}\nДата: {created_at}\n"
        res_text += "Позиции:\n"

        for item in menu_items:
            item_id = item["menu_item_id"]
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BACKEND_URL}/menu-items/{item_id}")
                item_data = response.json()
                item_name = item_data["name"]
            res_text += f"{item_name} - {item['quantity']} шт.\n"

        res_text += "\n"
    await message.reply(f"Список заказов:\n{res_text}")


@router.message(F.text == Buttons.MAKE_ORDER, ClientStates.main_menu)
async def make_order(message: types.Message, state: FSMContext):
    """Создание заказа."""
    await state.set_state(ClientStates.make_order)
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/menu-categories/")
        categories = response.json()

    res_text = "Выберите категорию:\n"
    await message.reply(res_text, reply_markup=generate_categories_keyboard(categories))
    await state.update_data(order_items=[])


@router.callback_query(F.data.startswith("select_category"))
async def select_category(callback_query: CallbackQuery, state: FSMContext):
    """Выбор категории."""
    category_id = int(callback_query.data.split(":")[1])
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/menu-items/?category_id={category_id}&is_available=true"
        )
        menu_items = response.json()
    if not menu_items:
        await callback_query.answer("В данной категории нет доступных позиций.")
        return

    res_text = "Выберите позицию:\n"
    await callback_query.message.edit_text(
        res_text, reply_markup=generate_menu_keyboard(menu_items)
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("select_item"))
async def select_item(callback_query: CallbackQuery, state: FSMContext):
    """Выбор позиции."""
    item_id = int(callback_query.data.split(":")[1])
    await state.update_data(selected_item_id=item_id, quantity=1)
    await callback_query.message.edit_text(
        "Выберите количество:", reply_markup=generate_quantity_keyboard(item_id, 1)
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("increase_quantity"))
async def increase_quantity(callback_query: CallbackQuery, state: FSMContext):
    """Увеличение количества."""
    data = await state.get_data()
    item_id = int(callback_query.data.split(":")[1])
    quantity = data.get("quantity", 1) + 1
    await state.update_data(quantity=quantity)
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_quantity_keyboard(item_id, quantity)
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("decrease_quantity"))
async def decrease_quantity(callback_query: CallbackQuery, state: FSMContext):
    """Уменьшение количества."""
    data = await state.get_data()
    item_id = int(callback_query.data.split(":")[1])
    quantity = max(1, data.get("quantity", 1) - 1)
    await state.update_data(quantity=quantity)
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_quantity_keyboard(item_id, quantity)
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("confirm_quantity"))
async def confirm_quantity(callback_query: CallbackQuery, state: FSMContext):
    """Подтверждение количества."""
    data = await state.get_data()
    item_id = int(callback_query.data.split(":")[1])
    quantity = data.get("quantity", 1)
    order_items = data.get("order_items", [])
    order_items.append({"menu_item_id": item_id, "quantity": quantity})
    await state.update_data(order_items=order_items, quantity=1)

    # Получаем обновленный список категорий
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/menu-categories/")
        categories = response.json()

    await callback_query.message.edit_text(
        "Позиция добавлена. Выберите следующую категорию или подтвердите заказ.",
        reply_markup=generate_categories_keyboard(categories),
    )
    await callback_query.answer()


@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback_query: CallbackQuery, state: FSMContext):
    """Подтверждение заказа."""
    data = await state.get_data()
    order_items = data.get("order_items", [])

    if not order_items:
        await callback_query.message.answer("Ваш заказ пуст.")
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/delivery-methods/")
        delivery_methods = response.json()

    res_text = "Выберите способ доставки:\n"
    await callback_query.message.reply(
        res_text, reply_markup=generate_delivery_methods_keyboard(delivery_methods)
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("select_delivery_method"))
async def select_delivery_method(callback_query: CallbackQuery, state: FSMContext):
    """Выбор способа доставки."""
    delivery_method_id = int(callback_query.data.split(":")[1])
    data = await state.get_data()
    order_items = data.get("order_items", [])
    user_id = callback_query.from_user.id

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/orders/",
            json={
                "user_id": user_id,
                "delivery_method_id": delivery_method_id,
                "status_id": OrderStatus.PENDING_ID,
                "items": order_items,
            },
        )
        response.raise_for_status()

    await state.clear()

    await state.set_state(ClientStates.main_menu)
    await callback_query.message.reply("Ваш заказ успешно оформлен!")
    await callback_query.answer()

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/roles/users/{Role.BARISTA_ID}")
        baristas_ids = response.json()["user_ids"]

    for barista in baristas_ids:
        await callback_query.message.bot.send_message(
            barista, f"Поступил новый заказ от пользователя {user_id}."
        )


@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback_query: CallbackQuery, state: FSMContext):
    """Отмена заказа."""
    await state.clear()
    await state.set_state(ClientStates.main_menu)
    await callback_query.message.reply("Ваш заказ был отменен.")
    await callback_query.answer()

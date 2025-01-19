from aiogram import Router, types
from aiogram.filters import Command, CommandStart
import httpx
from modules.envs.settings import settings
from bot.handlers.routers import admin_router
from modules.dataclasses.order_status import OrderStatus

router = Router()
admin_router.include_router(router)

BACKEND_URL = settings.bot.backend_url  # URL бэкенда

@router.message(CommandStart())
async def admin_panel(message: types.Message):
    """
    Вход в административную панель.
    """
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



@router.message(Command("orders"))
async def list_orders(message: types.Message):
    """
    Получает список заказов с бэкенда.
    """
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
                for order in orders
            )
            await message.reply(f"Список заказов:\n{order_list}")
        except httpx.RequestError as e:
            await message.reply(f"Ошибка при запросе заказов: {str(e)}")
        except httpx.HTTPStatusError as e:
            await message.reply(f"Ошибка на сервере: {e.response.text}")


@router.message(Command("set_status"))
async def set_order_status(message: types.Message):
    """
    Устанавливает новый статус заказа через бэкенд.
    """
    try:
        _, order_id, new_status = message.text.split()
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{BACKEND_URL}/orders/{order_id}/status",
                json={"status": new_status},
            )
            response.raise_for_status()

            if response.status_code == 200:
                await message.reply(f"Статус заказа ID {order_id} успешно обновлён на '{new_status}'.")
            else:
                await message.reply(f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}")
    except ValueError:
        await message.reply("Некорректный формат команды. Используйте: /set_status <order_id> <new_status>")
    except httpx.RequestError as e:
        await message.reply(f"Ошибка при обновлении статуса: {str(e)}")
    except httpx.HTTPStatusError as e:
        await message.reply(f"Ошибка на сервере: {e.response.text}")


@router.message(Command("menu"))
async def list_menu_items(message: types.Message):
    """
    Получает список товаров из меню с бэкенда.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BACKEND_URL}/products/")
            response.raise_for_status()
            products = response.json()

            if not products:
                await message.reply("Меню пусто.")
                return

            product_list = "\n".join(
                f"ID: {product['id']}, {product['name']} - {'в наличии' if product['in_stock'] else 'нет в наличии'}"
                for product in products
            )
            await message.reply(
                f"Меню:\n{product_list}\n\nВведите /set_stock <product_id> <1|0>, чтобы изменить статус товара."
            )
        except httpx.RequestError as e:
            await message.reply(f"Ошибка при запросе меню: {str(e)}")
        except httpx.HTTPStatusError as e:
            await message.reply(f"Ошибка на сервере: {e.response.text}")


@router.message(Command("add_product"))
async def add_product(message: types.Message):
    """
    Добавляет новый продукт в меню через бэкенд.
    """
    try:
        _, name, price, in_stock = message.text.split(maxsplit=3)
        price = float(price)
        in_stock = bool(int(in_stock))

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/products/",
                json={"name": name, "price": price, "in_stock": in_stock},
            )
            response.raise_for_status()

            if response.status_code == 200:
                await message.reply(f"Продукт '{name}' успешно добавлен.")
            else:
                await message.reply(f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}")
    except ValueError:
        await message.reply("Некорректный формат команды. Используйте: /add_product <name> <price> <in_stock>")
    except httpx.RequestError as e:
        await message.reply(f"Ошибка при добавлении продукта: {str(e)}")
    except httpx.HTTPStatusError as e:
        await message.reply(f"Ошибка на сервере: {e.response.text}")


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


@router.message(Command("delivery_methods"))
async def list_delivery_methods(message: types.Message):
    """
    Получает список способов доставки.
    """
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
                await message.reply(f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}")
    except ValueError:
        await message.reply("Некорректный формат команды. Используйте: /add_delivery <name>")
    except httpx.RequestError as e:
        await message.reply(f"Ошибка при добавлении способа доставки: {str(e)}")
    except httpx.HTTPStatusError as e:
        await message.reply(f"Ошибка на сервере: {e.response.text}")

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

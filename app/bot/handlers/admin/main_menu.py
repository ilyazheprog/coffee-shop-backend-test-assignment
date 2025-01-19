import json

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis

from bot.filters.basic import ButtonFilter
from bot.handlers.routers import admin_router
from bot.keyboards.basic import keyboard
from bot.keyboards.cqkb import create_users_paggination_keyboard
from bot.states.states import AdminState
from modules.crypto.main import decrypt
from modules.database.methods.keys_users import (
    add_key_by_location_and_device,
    get_key_details,
    get_keys_by_user,
)
from modules.database.methods.locations import get_location_by_domain
from modules.database.methods.servers import get_all_servers
from modules.database.methods.users import get_all_users
from modules.dataclasses import Buttons, Callbacks
from modules.envs import settings
from modules.formating import escape_markdown_v2
from modules.logs import logger
from modules.redis.main import set_state_with_redis
from modules.x_ui_api.async_api import AsyncXUI, convert_from_timestamp_ms
from modules.x_ui_api.consts import ClientFields

router = Router()
admin_router.include_router(router)


@router.message(Command("users"))
async def list_users(message: Message, redis: Redis):
    logger.info(f"Admin {message.from_user.id} requested a list of users.")

    loading_message = await message.answer(
        "🔄 Загрузка списка пользователей, пожалуйста, подождите..."
    )

    list_users_ = await get_all_users()

    chanks = []
    chunk_size = 10

    for i in range(0, len(list_users_), chunk_size):
        if i + chunk_size > len(list_users_):
            lst_users = list_users_[i:]
        else:
            lst_users = list_users_[i : i + chunk_size]

        chanks.append(
            "\n".join(
                [
                    escape_markdown_v2(
                        f"`{user.id}` - {'@' + user.username if user.username else 'Нет юзернейма'} - {'`' +str(user.refer_id)+'`' if user.refer_id else 'Не реферал'}"
                    )
                    for user in lst_users
                    if user.id != settings.bot.admin_id
                ]
            )
        )

    count_chanks = len(chanks)

    await redis.set("users", json.dumps(chanks))
    await loading_message.edit_text(
        f"Список пользователей:\n{chanks[0]}",
        reply_markup=await create_users_paggination_keyboard(
            1, 1, count_chanks, Callbacks.PAGE
        ),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@router.callback_query(F.data.startswith(Callbacks.PAGE))
async def users_paggination(query: CallbackQuery, redis: Redis):
    cb_data = query.data.split("_")
    current_page = int(cb_data[1])

    await query.message.edit_text(
        "🔄 Загрузка списка пользователей, пожалуйста, подождите..."
    )

    await query.answer()

    # Загружаем данные из Redis
    chanks_data = await redis.get("users")
    if chanks_data is None:
        logger.warning("Ключ 'users' отсутствует в Redis.")
        await query.message.edit_text(
            "Список пользователей недоступен. Попробуйте позже."
        )
        return

    # Десериализация данных
    try:
        chanks = json.loads(chanks_data)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {e}")
        await query.message.edit_text(
            "Ошибка обработки данных. Попробуйте позже.", show_alert=True
        )
        return

    # Проверка страницы
    if current_page < 0 or current_page >= len(chanks):
        logger.error(f"Некорректный номер страницы: {current_page}")
        await query.message.edit_text("Страница не найдена.", show_alert=True)
        return

    # Отправляем текущую страницу
    await query.message.edit_text(
        f"Список пользователей:\n{chanks[current_page]}",
        reply_markup=await create_users_paggination_keyboard(
            1, current_page, len(chanks), Callbacks.PAGE
        ),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, redis: Redis):
    await set_state_with_redis(state, redis, message, AdminState.main_menu)
    await message.answer("Привет, админ!", reply_markup=keyboard)
    logger.info(
        f"Admin {message.from_user.id} started the bot and entered the main menu."
    )


@router.message(ButtonFilter(Buttons.MAIN_MENU))
async def main_menu(message: Message, state: FSMContext, redis: Redis):
    await set_state_with_redis(state, redis, message, AdminState.main_menu)
    await message.answer("Главное меню", reply_markup=keyboard)
    logger.info(f"Admin {message.from_user.id} returned to the main menu.")


@router.message(ButtonFilter(Buttons.KEYS), AdminState.main_menu)
async def keys_menu(message: Message, state: FSMContext, redis: Redis):
    await set_state_with_redis(state, redis, message, AdminState.main_menu)
    keys = await get_keys_by_user(message.from_user.id)

    if not keys:
        await message.answer("У вас нет ключей")
        logger.info(f"User {message.from_user.id} has no keys.")
        return

    res = []
    for key in keys:
        key_details = await get_key_details(key)
        key_info = (
            f"- {key_details['date_first_payment']} — {key_details['date_next_payment']}\n"
            f"  Страна: {key_details['country']}, Город: {key_details['city']}\n"
            f"  Ключ: https://{key_details['domain']}/subs/{key_details['key_value']}\n"
            f"  Название ключа в панели: {key_details['name_from_pannel']}\n"
            f"  Устройство: {key_details['device_type']}\n"
            f"  Цена: {key_details['price']}, Активен: {'Да' if key_details['is_active'] else 'Нет'}"
        )
        res.append(key_info)

    keys_text = "\n\n".join(res)
    await message.answer(
        f"Ваши ключи:\n{keys_text}",
        parse_mode=ParseMode.MARKDOWN,
    )
    logger.info(f"User {message.from_user.id} viewed keys list.")


@router.message(F.text.startswith("/sk"))
async def sync_keys(message: Message):
    await message.answer("Синхронизация ключей")
    logger.info(f"User {message.from_user.id} started key synchronization process.")

    servers = [o["server"] for o in await get_all_servers() if o["server"].is_available]

    for server in servers:
        domain = server.domain
        login = decrypt(server.encrypt_login)
        password = decrypt(server.encrypt_password)
        panel_path = decrypt(server.encrypt_path_to_panel)

        async with AsyncXUI(
            domain=domain,
            panel_path=panel_path,
            login=login,
            password=password,
            inbound_id=1,
        ) as xui:
            keys = await xui.get_client_keys_all()
            for key in keys:
                key_id = key[ClientFields.ID]
                key_name = key[ClientFields.EMAIL]
                tg_id = key[ClientFields.TG_ID]
                if not tg_id:
                    continue
                subs = key[ClientFields.SUB_ID]
                expire_date = await convert_from_timestamp_ms(
                    key[ClientFields.EXPIRY_TIME]
                )
                device_type = "".join(
                    [sym for sym in key_name.split("-")[-1] if sym.isalpha()]
                )
                location_obj = await get_location_by_domain(domain)

                n_key_id = await add_key_by_location_and_device(
                    user_id=tg_id,
                    country=location_obj.country,
                    city=location_obj.city,
                    device_type=device_type,
                    key_value=subs,
                    price=100,
                    expire_date=expire_date,
                    key_id_from_pannel=key_id,
                    name_from_pannel=key_name,
                )
                if not n_key_id:
                    logger.error(f"Failed to add key from XUI: {key_id}")
                    await message.answer(f"Ошибка добавления ключа: {key_id}")
            logger.info(f"Keys successfully synchronized for server {domain}.")
            await message.answer(f"Ключи успешно синхронизированы для сервера {domain}")

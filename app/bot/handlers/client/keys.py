import json
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis

from bot.filters.basic import ButtonFilter, DeviceFilter
from bot.handlers.routers import client_router
from bot.keyboards.basic import (
    all_devices_keyboard,
    available_locations_keyboard,
    confirm_keyboard,
    keys_client_keyboard,
)
from bot.keyboards.cqkb import create_expand_keys_keyboard
from bot.states.states import ClientState
from modules.crypto import decrypt
from modules.database.methods import (
    add_key_by_location_and_device,
    get_device_type_by_alt_name,
    get_keys_by_user,
)
from modules.database.methods.keys_users import (
    delete_key_user_by_id,
    get_device_type_by_key,
    get_id_key_from_pannel,
    get_key_count_by_user_and_device_type,
    get_key_details,
    get_key_details_by_user_id_and_country_and_name_and_device,
    update_data_key_from_xui,
    update_key_user,
)
from modules.database.methods.locations import get_location_by_country_and_city
from modules.database.methods.servers import get_all_servers, get_server_by_id
from modules.database.methods.users import (
    add_balance,
    get_user_balance,
    get_user_by_tg_id,
)
from modules.dataclasses import Buttons
from modules.dataclasses.callbacks import Callbacks
from modules.envs.settings import settings
from modules.logs import logger
from modules.random_strings.main import generate_subscription
from modules.redis.main import set_state_with_redis
from modules.x_ui_api import AsyncXUI
from modules.x_ui_api.consts import ClientFields

router = Router()
client_router.include_router(router)


@router.message(ButtonFilter(Buttons.KEYS), ClientState.main_menu)
async def keys_menu(message: Message, state: FSMContext, redis: Redis):
    await set_state_with_redis(state, redis, message, ClientState.keys_menu)
    keys = await get_keys_by_user(message.from_user.id)

    if not keys:
        await message.answer("У вас нет ключей", reply_markup=keys_client_keyboard)
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
        reply_markup=keys_client_keyboard,
        parse_mode=ParseMode.MARKDOWN,
    )
    logger.info(f"User {message.from_user.id} viewed keys list.")


@router.message(ButtonFilter(Buttons.BUY_KEY), ClientState.keys_menu)
async def buy_key(message: Message, state: FSMContext, redis: Redis):
    await set_state_with_redis(state, redis, message, ClientState.choise_location)
    await message.answer(
        "Покупка ключа.\nВыберите локацию",
        reply_markup=await available_locations_keyboard(),
    )
    logger.info(f"User {message.from_user.id} started key purchase process.")


@router.message(ClientState.choise_location)
async def choise_device(message: Message, state: FSMContext, redis: Redis):
    location_text = message.text
    location_obj = await get_location_by_country_and_city(*location_text.split("/"))

    if not location_obj:
        logger.warning(
            f"User {message.from_user.id} selected an invalid location: {location_text}"
        )
        await message.answer("Неверная локация, выберите правильную.")
        return

    await state.update_data({"location": location_text, "location_id": location_obj.id})
    await set_state_with_redis(state, redis, message, ClientState.choise_device)
    await message.answer(
        "Выберите устройство",
        reply_markup=await all_devices_keyboard(),
    )
    logger.info(f"User {message.from_user.id} selected location: {location_text}")


@router.message(DeviceFilter(), ClientState.choise_device)
async def confitm(message: Message, state: FSMContext, redis: Redis):
    device = message.text
    device_obj = await get_device_type_by_alt_name(device)

    if not device_obj:
        await message.answer("Устройство не найдено, выберите из списка.")
        logger.warning(
            f"User {message.from_user.id} selected an invalid device: {device}"
        )
        return

    data = await state.get_data()
    await state.set_data(
        {
            "location": data["location"],
            "location_id": data["location_id"],
            "device_alt": device_obj.alt_name,
            "device": device_obj.type,
            "device_id": device_obj.id,
        }
    )

    await set_state_with_redis(state, redis, message, ClientState.confirm_get_key)
    await message.answer(
        f"Вы выбрали:\nЛокация: {data['location']}\nУстройство: {device}\n\nВерно?",
        reply_markup=confirm_keyboard,
    )
    logger.info(f"User {message.from_user.id} selected device: {device}")


@router.message(ButtonFilter(Buttons.CORRECT), ClientState.confirm_get_key)
async def get_key(message: Message, state: FSMContext, redis: Redis):
    data = await state.get_data()
    location = data["location"]
    device_alt = data["device_alt"]

    await set_state_with_redis(state, redis, message, ClientState.get_key)
    await message.answer(f"Получение ключа для {location}/{device_alt}")

    user = await get_user_by_tg_id(message.from_user.id)
    price = settings.key.price

    if user["personal_discount_value"]:
        if user["discount_type"] == "%":
            price = price * (1 - user["personal_discount_value"] / 100)
        else:
            price -= user["personal_discount_value"]

    if (await get_user_balance(message.from_user.id)) < price:
        await message.answer("Недостаточно средств")
        logger.warning(
            f"User {message.from_user.id} tried to buy a key but had insufficient funds."
        )
        return

    await add_balance(message.from_user.id, -price)
    logger.info(f"User {message.from_user.id} bought a key for {price}.")
    device_obj = await get_device_type_by_alt_name(device_alt)

    res = await add_key_by_location_and_device(
        user_id=message.chat.id,
        country=location.split("/")[0],
        city=location.split("/")[1],
        device_type=device_obj.type,
        key_value=generate_subscription(),
        price=price,
    )

    if res:
        server_id = res[0]
        key_obj = res[1]
        key = res[2]
        server, _ = (await get_server_by_id(server_id)).values()

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
            subs = key_obj.key_value
            tg_id = key_obj.user_id
            expired = key_obj.date_next_payment
            device_dict = await get_device_type_by_key(key_obj)
            count = (
                await get_key_count_by_user_and_device_type(tg_id, device_dict["type"])
            ) + 1
            name_key = f"{tg_id}-{device_dict['type']}{count}"

            if key_id_xui := await xui.add_client_key(name_key, tg_id, subs, expired):
                await message.answer(
                    f"Ключ успешно добавлен: `{key}`", parse_mode=ParseMode.MARKDOWN_V2
                )
                await message.answer(
                    f"Если не знаешь как пользоваться, держи инструкцию: {settings.bot.manual_connect_link}\nПомощь: @{settings.bot.admin_username}"
                )
                await update_data_key_from_xui(
                    key_id=key_obj.id, key_id_xui=key_id_xui, name_from_xui=name_key
                )
                logger.info(
                    f"Key successfully added for user {message.from_user.id}. Key: {key}"
                )
            else:
                await message.answer("Ошибка добавления ключа")
                await delete_key_user_by_id(key_obj.id)
                logger.error(
                    f"Failed to add key for user {message.from_user.id}. Key deletion initiated."
                )


@router.message(ButtonFilter(Buttons.RENEW_KEY), ClientState.keys_menu)
async def renew_key(message: Message, state: FSMContext, redis: Redis):
    await set_state_with_redis(state, redis, message, ClientState.renew_keys)
    keys = await get_keys_by_user(message.from_user.id)

    if not keys:
        await message.answer("У вас нет ключей", reply_markup=keys_client_keyboard)
        logger.info(f"User {message.from_user.id} has no keys.")
        return

    choise_mask = [False] * len(keys)
    await redis.set(f"{message.from_user.id}:choise_mask", json.dumps(choise_mask))

    titles_btns = []

    for key in keys:
        key_details = await get_key_details(key)
        titles_btns.append(
            f'{key_details["country"]}/{key_details["device_type"]}/{key_details["name_from_pannel"]}'
        )

    await redis.set(f"{message.from_user.id}:titles_btns", json.dumps(titles_btns))
    await message.answer(
        f"Выберите ключи для продления",
        reply_markup=await create_expand_keys_keyboard(
            titles_btns, choise_mask, Callbacks.RENEW_KEYS
        ),
    )
    logger.info(f"User {message.from_user.id} started key renewal process.")


@router.callback_query(F.data == Callbacks.RENEW_KEYS_DONE)
async def renew_keys_done(query: CallbackQuery, redis: Redis):
    choise_mask = json.loads(await redis.get(f"{query.from_user.id}:choise_mask"))
    titles_btns = json.loads(await redis.get(f"{query.from_user.id}:titles_btns"))

    keys = []
    total_price = 0
    for i, title in enumerate(titles_btns):
        if not choise_mask[i]:
            continue
        country, device, name = title.split("/")
        key_details = await get_key_details_by_user_id_and_country_and_name_and_device(
            query.from_user.id, country, name, device
        )
        date_next_payment = key_details["date_next_payment"] + timedelta(days=30)

        key_id_from_pannel = key_details["id_from_pannel"]
        domain = key_details["domain"]
        login = decrypt(key_details["encrypt_login"])
        password = decrypt(key_details["encrypt_password"])
        panel_path = decrypt(key_details["encrypt_path_to_panel"])
        price = key_details["price"]
        total_price += price
        keys.append(
            dict(
                key_id=key_details["id"],
                key_id_from_pannel=key_id_from_pannel,
                domain=domain,
                login=login,
                password=password,
                panel_path=panel_path,
                price=price,
                date_next_payment=date_next_payment,
            )
        )

    if (user_bal := await get_user_balance(query.from_user.id)) < total_price:
        await query.message.edit_text(
            f"Недостаточно средств! Пополните баланс минимум на {total_price-user_bal}."
        )
        logger.warning(
            f"User {query.from_user.id} tried to renew a key but had insufficient funds."
        )
        return query

    await add_balance(query.from_user.id, -total_price)
    await query.message.edit_text(
        f"С вашего баланса списано {total_price} за продление ключей. Идёт процесс продления, ожидайте."
    )
    logger.info(f"User {query.from_user.id} charged {total_price} for renewing keys.")

    is_done = True
    count_keys = len(keys)
    count_keys_renewed = 0
    refund_price = 0

    for key in keys:
        async with AsyncXUI(
            domain=key["domain"],
            panel_path=key["panel_path"],
            login=key["login"],
            password=key["password"],
            inbound_id=1,
        ) as xui:
            try:
                if await xui.update_date(
                    id_key=key["key_id_from_pannel"], new_date=key["date_next_payment"]
                ):
                    logger.info(
                        f"User {query.from_user.id} renewed key {key['key_id_from_pannel']}. XUI updated."
                    )
                    await update_key_user(
                        key["key_id"], new_date_next_payment=key["date_next_payment"]
                    )
                    logger.info(
                        f"User {query.from_user.id} renewed key {key['key_id_from_pannel']}. Database updated."
                    )
                    count_keys_renewed += 1
                else:
                    logger.error(
                        f"Failed to renew key {key['key_id_from_pannel']} for user {query.from_user.id}."
                    )
                    is_done = False
                    refund_price += key["price"]

            except Exception as e:
                logger.exception(
                    f"An error occurred while renewing key {key['key_id_from_pannel']} for user {query.from_user.id}: {e}"
                )
                is_done = False
                refund_price += key["price"]

    if is_done:
        await query.message.edit_text("Ключи продлены на 30 дней")
    else:
        await add_balance(query.from_user.id, refund_price)
        await query.message.edit_text(
            f"Вернули {refund_price}. Продлено {count_keys_renewed} из {count_keys} выбраных ключей. Напишите @ilyazheprog"
        )
        logger.info(
            f"To user {query.from_user.id} refunded {refund_price} for fail renewing keys."
        )


@router.callback_query(F.data == Callbacks.RENEW_KEYS_ALL)
async def renew_keys_all(query: CallbackQuery, redis: Redis):
    titles_btns = json.loads(await redis.get(f"{query.from_user.id}:titles_btns"))
    choise_mask = [True] * len(titles_btns)
    await redis.set(f"{query.from_user.id}:choise_mask", json.dumps(choise_mask))
    await query.answer()

    await query.message.edit_reply_markup(
        reply_markup=await create_expand_keys_keyboard(
            titles_btns, choise_mask, Callbacks.RENEW_KEYS
        )
    )


@router.callback_query(F.data == Callbacks.RENEW_KEYS_RESET)
async def renew_keys_reset(query: CallbackQuery, redis: Redis):
    titles_btns = json.loads(await redis.get(f"{query.from_user.id}:titles_btns"))
    choise_mask = [False] * len(titles_btns)
    await redis.set(f"{query.from_user.id}:choise_mask", json.dumps(choise_mask))
    await query.answer()
    await query.message.edit_reply_markup(
        reply_markup=await create_expand_keys_keyboard(
            titles_btns, choise_mask, Callbacks.RENEW_KEYS
        )
    )


@router.callback_query(F.data.startswith(Callbacks.RENEW_KEYS))
async def renew_keys(query: CallbackQuery, redis: Redis):
    cb_data = query.data.split("_")
    choise_mask = json.loads(await redis.get(f"{query.from_user.id}:choise_mask"))
    choise_mask[int(cb_data[-1])] = not choise_mask[int(cb_data[-1])]
    await redis.set(f"{query.from_user.id}:choise_mask", json.dumps(choise_mask))
    await query.answer()

    titles_btns = json.loads(await redis.get(f"{query.from_user.id}:titles_btns"))
    await query.message.edit_reply_markup(
        reply_markup=await create_expand_keys_keyboard(
            titles_btns, choise_mask, Callbacks.RENEW_KEYS
        )
    )


@router.message(ButtonFilter(Buttons.CLEAR_IP_LIST), ClientState.keys_menu)
async def clear_ip_list(message: Message, state: FSMContext):
    keys = await get_keys_by_user(message.from_user.id)

    if not keys:
        await message.answer(
            "У вас нет ключей для очистки списка IP.", reply_markup=keys_client_keyboard
        )
        logger.info(f"User {message.from_user.id} has no keys to clear the IP list.")
        return

    active_keys = []

    for key in keys:
        key_details = await get_key_details(key)
        active_keys.append(key_details)

    for key_details in active_keys:
        domain = key_details["domain"]
        login = decrypt(key_details["encrypt_login"])
        password = decrypt(key_details["encrypt_password"])
        panel_path = decrypt(key_details["encrypt_path_to_panel"])

        async with AsyncXUI(
            domain=domain,
            panel_path=panel_path,
            login=login,
            password=password,
            inbound_id=1,
        ) as xui:
            if not await xui.clear_ip_list(id_key=key_details["id_from_pannel"]):
                await message.answer(
                    f"Ошибка очистки списка IP для ключа {key_details['name_from_pannel']}."
                )
                logger.error(
                    f"Failed to clear IP list for key {key_details['name_from_pannel']} for user {message.from_user.id}."
                )

    await message.answer(f"Список IP успешно очищен для всех ключей.")
    logger.info(
        f"IP list successfully cleared for all keys for user {message.from_user.id}."
    )

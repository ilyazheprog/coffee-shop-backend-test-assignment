from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from redis.asyncio import Redis

from bot.filters.basic import ButtonFilter, DomainFilter, Regexp
from bot.handlers.routers import admin_router
from bot.keyboards.basic import (
    admin_server_keyboard,
    all_locations_keyboard,
    cancel_keyboard,
    confirm_keyboard,
    keyboard,
)
from bot.states.states import AdminState
from modules.database.methods import (
    add_server as add_server_db,
    get_all_servers,
    get_location_by_country_and_city,
)
from modules.database.methods.servers import (
    change_server_availability,
    get_all_servers_with_locations,
)
from modules.dataclasses import Buttons
from modules.logs import logger
from modules.redis.main import clear_state_with_redis, set_state_with_redis

router = Router()
admin_router.include_router(router)


@router.message(ButtonFilter(Buttons.SERVERS), AdminState.main_menu)
async def server_menu(message: Message, state: FSMContext, redis: Redis):
    await set_state_with_redis(state, redis, message, AdminState.server_menu)
    await message.answer("Меню серверов", reply_markup=admin_server_keyboard)
    logger.info(f"Admin {message.from_user.id} accessed the server menu.")


@router.message(ButtonFilter(Buttons.LIST_SERVERS), AdminState.server_menu)
async def list_servers(message: Message):
    servers = await get_all_servers_with_locations()

    if not servers:
        await message.answer("Список серверов пуст!", reply_markup=admin_server_keyboard)
        logger.info(f"Admin {message.from_user.id} accessed an empty server list.")
        return

    servers_str = "\n".join(
        [
            f"id:`{server['server'].id}`\nДомен: {server['server'].domain}\n"
            f"Локация: {server['location'].country}/{server['location'].city}\n"
            f"Количество ключей: {server['key_count']}\n"
            f"Ограничение на количество ключей: {server['server'].limit_count_keys}\n"
            f"Нагрузка: {server['key_count']/server['server'].limit_count_keys*100}%\n"
            f"{'🔴' if not server['server'].is_available else '🟢'}"
            for server in servers
        ]
    )
    await message.answer(
        f"Список серверов:\n{servers_str}", reply_markup=admin_server_keyboard
    )
    logger.info(f"Admin {message.from_user.id} viewed server list.")


@router.message(F.text.startswith("/as"), AdminState.server_menu)
async def available_server(message: Message, redis: Redis):
    server_id = int(message.text.split()[1])

    if not await change_server_availability(server_id, True):
        await message.answer("Сервер не найден!", reply_markup=admin_server_keyboard)
        logger.error(
            f"Admin {message.from_user.id} tried to access non-existing server: {server_id}"
        )
        return

    await message.answer(
        f"Сервер {server_id} теперь доступен!",
        reply_markup=admin_server_keyboard,
    )
    logger.info(
        f"Admin {message.from_user.id} changed availability for server: {server_id}."
    )


@router.message(F.text.startswith("/us"), AdminState.server_menu)
async def unavailable_server(message: Message, redis: Redis):
    server_id = int(message.text.split()[1])

    if not await change_server_availability(server_id, False):
        await message.answer("Сервер не найден!", reply_markup=admin_server_keyboard)
        logger.error(
            f"Admin {message.from_user.id} tried to access non-existing server: {server_id}"
        )
        return

    await message.answer(
        f"Сервер {server_id} теперь недоступен!",
        reply_markup=admin_server_keyboard,
    )
    logger.info(
        f"Admin {message.from_user.id} changed availability for server: {server_id}."
    )


@router.message(ButtonFilter(Buttons.ADD_SERVER), AdminState.server_menu)
async def add_server(message: Message, state: FSMContext, redis: Redis):
    await set_state_with_redis(state, redis, message, AdminState.enter_server_domain)
    await message.answer(
        "Добавление сервера. Введите домен сервера", reply_markup=cancel_keyboard
    )
    logger.info(f"Admin {message.from_user.id} started adding a new server.")


@router.message(DomainFilter(), AdminState.enter_server_domain)
async def enter_server_domain(message: Message, state: FSMContext, redis: Redis):
    domain = message.text.strip()
    await set_state_with_redis(state, redis, message, AdminState.choise_location)
    await state.update_data(domain=domain)
    await message.answer(
        "Выберите локацию сервера", reply_markup=await all_locations_keyboard()
    )
    logger.info(f"Admin {message.from_user.id} entered server domain: {domain}")


@router.message(AdminState.enter_server_domain)
async def incorrect_domain(message: Message):
    await message.answer(
        "Неверный формат! Введите домен сервера", reply_markup=cancel_keyboard
    )
    logger.warning(
        f"Admin {message.from_user.id} entered an incorrect server domain format."
    )


@router.message(
    Regexp("^[A-Za-zА-Яа-яЁё\s]+\/[A-Za-zА-Яа-яЁё\s]+$"), AdminState.choise_location
)
async def choise_location(message: Message, state: FSMContext, redis: Redis):
    country, city = map(lambda x: x.strip().title(), message.text.split("/"))
    location = await get_location_by_country_and_city(country, city)

    if not location:
        await message.answer(
            f"Локация {country}/{city} не найдена! Попробуйте снова.",
            reply_markup=cancel_keyboard,
        )
        logger.warning(
            f"Admin {message.from_user.id} tried to select a non-existing location: {country}/{city}"
        )
        return

    await set_state_with_redis(
        state, redis, message, AdminState.enter_server_path_to_panel
    )
    await state.update_data(country=country, city=city)

    await message.answer(
        "Введите путь к панели управления сервером", reply_markup=cancel_keyboard
    )
    logger.info(f"Admin {message.from_user.id} selected location: {country}/{city}.")


@router.message(AdminState.enter_server_path_to_panel)
async def enter_server_path_to_panel(message: Message, state: FSMContext, redis: Redis):
    path_to_panel = message.text.strip()
    await set_state_with_redis(state, redis, message, AdminState.enter_server_login)
    await state.update_data(path_to_panel=path_to_panel)
    await message.answer(
        "Введите логин от панели управления сервером", reply_markup=cancel_keyboard
    )
    logger.info(f"Admin {message.from_user.id} entered panel path.")


@router.message(AdminState.enter_server_login)
async def enter_server_login(message: Message, state: FSMContext, redis: Redis):
    login = message.text.strip()
    await set_state_with_redis(state, redis, message, AdminState.enter_server_password)
    await state.update_data(login=login)
    await message.answer(
        "Введите пароль от панели управления сервером", reply_markup=cancel_keyboard
    )
    logger.info(f"Admin {message.from_user.id} entered login.")


@router.message(AdminState.enter_server_password)
async def enter_server_password(message: Message, state: FSMContext, redis: Redis):
    password = message.text.strip()
    await set_state_with_redis(
        state, redis, message, AdminState.enter_server_limit_count_keys
    )
    await state.update_data(password=password)
    await message.answer(
        "Введите ограничение на количество ключей для сервера",
        reply_markup=cancel_keyboard,
    )
    logger.info(f"Admin {message.from_user.id} entered password.")


@router.message(Regexp("^\d+$"), AdminState.enter_server_limit_count_keys)
async def enter_server_limit_count_keys(
    message: Message, state: FSMContext, redis: Redis
):
    limit_count_keys = int(message.text)
    await state.update_data(limit_count_keys=limit_count_keys)
    await set_state_with_redis(state, redis, message, AdminState.confirm_server_add)
    await message.answer(
        "Подтверждение добавления сервера", reply_markup=confirm_keyboard
    )
    logger.info(f"Admin {message.from_user.id} entered key limit: {limit_count_keys}.")


@router.message(ButtonFilter(Buttons.CORRECT), AdminState.confirm_server_add)
async def confirm_server_add(message: Message, state: FSMContext, redis: Redis):
    data = await state.get_data()
    domain = data.get("domain")
    path_to_panel = data.get("path_to_panel")
    login = data.get("login")
    password = data.get("password")
    country = data.get("country")
    city = data.get("city")
    limit_count_keys = data.get("limit_count_keys")

    location = await get_location_by_country_and_city(country, city)

    if not location:
        await message.answer(
            f"Локация {country}/{city} не найдена! Попробуйте снова.",
            reply_markup=cancel_keyboard,
        )
        logger.warning(
            f"Admin {message.from_user.id} tried to add a server with non-existing location: {country}/{city}"
        )
        return

    success = await add_server_db(
        domain=domain,
        path_to_panel=path_to_panel,
        login=login,
        password=password,
        location_id=location.id,
        limit_count_keys=limit_count_keys,
    )

    if not success:
        await message.answer("Ошибка при добавлении сервера!", reply_markup=keyboard)
        logger.error(f"Error adding server {domain} for admin {message.from_user.id}.")
        return

    await clear_state_with_redis(state, redis, message)
    await set_state_with_redis(state, redis, message, AdminState.main_menu)
    await message.answer(f"Сервер {domain} успешно добавлен!", reply_markup=keyboard)
    logger.info(f"Admin {message.from_user.id} successfully added server {domain}.")


@router.message(ButtonFilter(Buttons.CANCEL), AdminState.confirm_server_add)
async def cancel_add_server(message: Message, state: FSMContext, redis: Redis):
    await set_state_with_redis(state, redis, message, AdminState.server_menu)
    await message.answer("Отменено", reply_markup=admin_server_keyboard)
    logger.info(f"Admin {message.from_user.id} canceled server addition.")

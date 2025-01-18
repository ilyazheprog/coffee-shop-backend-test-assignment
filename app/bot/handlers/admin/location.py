import logging

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from redis.asyncio import Redis

from bot.filters.basic import ButtonFilter, Regexp
from bot.handlers.routers import admin_router
from bot.keyboards.basic import (
    admin_location_keyboard,
    all_locations_keyboard,
    cancel_keyboard,
    confirm_keyboard,
    keyboard,
)
from bot.states.states import AdminState
from modules.database.methods import (
    add_location as add_location_db,
    delete_location_by_country_and_city as delete_location_db,
    get_all_locations,
)
from modules.database.methods.locations import change_availability_status
from modules.dataclasses import Buttons
from modules.logs import logger
from modules.redis.main import set_state_with_redis

router = Router()
admin_router.include_router(router)

LOCATION_REGEXP = "^[A-Za-zА-Яа-яЁё\s]+\/[A-Za-zА-Яа-яЁё\s]+$"


@router.message(ButtonFilter(Buttons.LOCATIONS), AdminState.main_menu)
async def location_menu(message: Message, state: FSMContext, redis: Redis):
    await set_state_with_redis(state, redis, message, AdminState.location_menu)
    locs = await get_all_locations()

    logger.info(f"Admin {message.from_user.id} get all locations.")

    if not locs:
        await message.answer("Список локаций пуст!", reply_markup=admin_location_keyboard)
        logging.warning(f"Admin {message.from_user.id} accessed empty location list.")
        return

    locations_str = "\n".join(
        [
            f"[{location.id}] {location.country}/{location.city} {'🔴' if not location.is_available else '🟢'}"
            for location in locs
        ]
    )
    await message.answer(
        f"Локации:\n{locations_str}", reply_markup=admin_location_keyboard
    )
    logging.info(f"Admin {message.from_user.id} accessed the location menu.")


@router.message(F.text.startswith("/al"), AdminState.location_menu)
async def available_location(message: Message, state: FSMContext, redis: Redis):
    location_id = int(message.text.split()[1])

    if not await change_availability_status(location_id, True):
        await message.answer("Локация не найдена!", reply_markup=admin_location_keyboard)
        logging.warning(
            f"Admin {message.from_user.id} tried to access non-existing location: {location_id}"
        )
        return

    await set_state_with_redis(state, redis, message, AdminState.location_menu)
    await message.answer(
        f"Локация {location_id} теперь доступна!",
        reply_markup=admin_location_keyboard,
    )
    logger.info(
        f"Admin {message.from_user.id} changed availability for location: {location_id}"
    )

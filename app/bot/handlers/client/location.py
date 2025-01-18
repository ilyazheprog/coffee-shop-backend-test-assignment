from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from redis.asyncio import Redis

from bot.filters.basic import ButtonFilter
from bot.handlers.routers import client_router
from bot.keyboards.basic import client_location_keyboard
from bot.states.states import ClientState
from modules.database.methods import get_available_locations
from modules.dataclasses import Buttons
from modules.logs import logger
from modules.redis.main import set_state_with_redis

router = Router()
client_router.include_router(router)


@router.message(ButtonFilter(Buttons.LOCATIONS), ClientState.main_menu)
async def location_menu(message: Message, state: FSMContext, redis: Redis):
    # Устанавливаем состояние через Redis
    await set_state_with_redis(state, redis, message, ClientState.location_menu)

    locs = await get_available_locations()
    if not locs:
        await message.answer(
            "Нет доступных локаций на данный момент.",
            reply_markup=client_location_keyboard,
        )
        logger.warning(
            f"User {message.from_user.id} tried to access locations, but no locations were found."
        )
        return

    res = [f"- **{loc.country}/{loc.city}**" for loc in locs]
    locations_str = "\n".join(res)
    await message.answer(
        f"Доступные локации:\n{locations_str}",
        reply_markup=client_location_keyboard,
        parse_mode=ParseMode.MARKDOWN,
    )
    logger.info(f"User {message.from_user.id} accessed locations: {locations_str}")

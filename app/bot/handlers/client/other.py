from aiogram import Bot, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message
from redis.asyncio import Redis

from bot.filters.basic import ButtonFilter
from bot.handlers.routers import client_router
from bot.keyboards.basic import main_menu_client_keyboard
from bot.states.states import ClientState
from modules.database.methods import add_user, is_user_exists
from modules.dataclasses import Buttons, Role
from modules.envs.settings import settings
from modules.logs import logger
from modules.redis.main import set_state_with_redis

router = Router()


@router.message()
async def unrecognized_message(message: Message):
    logger.warning(
        f"User {message.from_user.id} sent an unrecognized message: {message.text}"
    )
    await message.answer(
        "Я не знаю, что ответить на это сообщение. Возможно, я обновился. Нажмите /start, чтобы начать работу с ботом."
    )

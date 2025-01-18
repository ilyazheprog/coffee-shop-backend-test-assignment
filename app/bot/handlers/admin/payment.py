from aiogram import Bot, F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

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
from modules.database.methods import add_balance as add_balance_db, update_config
from modules.database.methods.locations import change_availability_status
from modules.dataclasses import Buttons
from modules.dataclasses.configs import Configs
from modules.logs import logger

router = Router()
admin_router.include_router(router)


@router.message(F.text.startswith("/abal"))
async def add_balance(message: Message, state: FSMContext, bot: Bot):
    user_id, money = message.text.split()[1:]

    await add_balance_db(int(user_id), float(money))
    logger.info(f"Admin {message.from_user.id} added {money} to user {user_id}")
    await message.answer(f"Баланс пользователя {user_id} пополнен на {money} руб.")

    try:
        await bot.send_message(
            int(user_id),
            f"Ваш баланс пополнен админом на {money} руб.",
            parse_mode=ParseMode.HTML,
        )
    except TelegramForbiddenError:
        logger.error(f"User {user_id} blocked the bot.")


@router.message(F.text.startswith("/up"))
async def unlock_payment(message: Message, state: FSMContext):
    await update_config(Configs.RECEIVE_PAYMENT, Configs.RECEIVE_PAYMENT_TRUE)
    logger.info(f"Admin {message.from_user.id} unlocked payments.")
    await message.answer("Платежи разблокированы!")


@router.message(F.text.startswith("/lp"))
async def lock_payment(message: Message, state: FSMContext):
    await update_config(Configs.RECEIVE_PAYMENT, Configs.RECEIVE_PAYMENT_FALSE)
    logger.info(f"Admin {message.from_user.id} locked payments.")
    await message.answer("Платежи заблокированы!")

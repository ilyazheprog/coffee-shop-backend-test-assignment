import json

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis

from bot.filters.basic import ButtonFilter
from bot.handlers.routers import client_router
from bot.keyboards.basic import main_menu_client_keyboard
from bot.keyboards.cqkb import create_users_paggination_keyboard
from bot.states.states import ClientState
from modules.database.methods import get_referals
from modules.dataclasses import Buttons
from modules.dataclasses.callbacks import Callbacks
from modules.envs.settings import settings
from modules.formating import escape_markdown_v2
from modules.logs import logger

router = Router()
client_router.include_router(router)


@router.message(ButtonFilter(Buttons.REFERAL_LINK), ClientState.main_menu)
async def referal_link(message: Message):
    await message.answer(
        f"Ваша реферальная ссылка: `t.me/{settings.bot.username}?start={message.from_user.id}`",
        reply_markup=main_menu_client_keyboard,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    logger.info(f"To user {message.from_user.id} sent the referal link")


@router.message(ButtonFilter(Buttons.MY_REFERALS), ClientState.main_menu)
async def list_referals(message: Message, redis: Redis):
    logger.info(f"User {message.from_user.id} requested a list of referals.")

    loading_message = await message.answer(
        "🔄 Загрузка списка пользователей, пожалуйста, подождите..."
    )

    list_users_ = await get_referals(message.from_user.id)
    if not list_users_:
        await message.answer("У вас нет рефералов")
        logger.info(f"User {message.from_user.id} has no referals")
        return

    chanks = []
    chunk_size = 10

    for i in range(0, len(list_users_), chunk_size):
        lst_users = list_users_[i : i + chunk_size]

        chanks.append(
            "\n".join(
                [
                    escape_markdown_v2(
                        f"`{user['user'].id}` - {'@' + user['user'].username if user['user'].username else 'Нет юзернейма'}"
                    )
                    for user in lst_users
                ]
            )
        )

    count_chanks = len(chanks)

    await redis.set(f"{message.from_user.id}:referals", json.dumps(chanks))
    await loading_message.edit_text(
        f"Список рефералов:\n{chanks[0]}",
        reply_markup=await create_users_paggination_keyboard(
            1, 1, count_chanks, Callbacks.REFERALS
        ),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@router.callback_query(F.data.startswith(Callbacks.REFERALS))
async def users_paggination(query: CallbackQuery, redis: Redis):
    cb_data = query.data.split("_")
    current_page = int(cb_data[1])
    loading_message = await query.message.answer(
        "🔄 Загрузка списка пользователей, пожалуйста, подождите..."
    )
    await query.answer()

    # Загружаем данные из Redis
    chanks_data = await redis.get(f"{query.from_user.id}:referals")
    if chanks_data is None:
        logger.warning(f"Ключ '{query.from_user.id}:referals' отсутствует в Redis.")
        await loading_message.edit_text(
            "Список пользователей недоступен. Попробуйте позже."
        )
        return

    # Десериализация данных
    try:
        chanks = json.loads(chanks_data)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {e}")
        await loading_message.edit_text("Ошибка обработки данных. Попробуйте позже.")
        return

    # Проверка страницы
    if current_page < 0 or current_page >= len(chanks):
        logger.error(f"Некорректный номер страницы: {current_page}")
        await loading_message.edit_text("Страница не найдена.")
        return

    await loading_message.edit_text(
        f"Список рефералов:\n{chanks[current_page]}",
        reply_markup=await create_users_paggination_keyboard(
            1, current_page, len(chanks), Callbacks.REFERALS
        ),
        parse_mode=ParseMode.MARKDOWN_V2,
    )

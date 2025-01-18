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
client_router.include_router(router)


@router.message(CommandStart())
async def start(
    message: Message, bot: Bot, state: FSMContext, redis: Redis, command: CommandObject
):
    args = command.args
    if args and not args.isdigit():
        logger.warning(
            f"Invalid referral ID provided by user {message.from_user.id}: {args}"
        )

    logger.info(f"User {message.from_user.id} started the bot with args: {args}")

    if not await is_user_exists(message.from_user.id):
        refer_id = int(args) if args and args.isdigit() else None
        success = await add_user(
            tg_id=message.from_user.id,
            refer_id=refer_id,
            username=message.from_user.username,
            role_id=Role.CLIENT,
        )
        if not success:
            logger.info(
                f"User {message.from_user.id} unsuccessfully added to the database with refer_id: {refer_id}"
            )
            await message.answer(text="Не существует пользователя с таким реферальным ID")
            await add_user(
                tg_id=message.from_user.id,
                username=message.from_user.username,
                role_id=Role.CLIENT,
            )
            logger.info(
                f"User {message.from_user.id} added to the database without refer_id"
            )
        else:
            logger.info(
                f"User {message.from_user.id} added to the database with refer_id: {refer_id}"
            )
    await send_offer_agreement(message, bot, state, redis)
    await message.answer(
        "Валюта бота: рубль российский\n"
        "Стоимость услуг (без скидки): 150 рублей\n"
        "Вы можете вернуть средства с баланса в любой момент в полном объёме.\n"
        "Возврат средств за используемый ключ рассчитывается по формуле:\n"
        "(цена ключа) - (цена ключа / 30) * (количество использованных дней).\n\n"
        "Примечание: использование ключа округляется в большую сторону. Например, если ключ был использован хотя бы одну секунду, это считается как полный день."
    )


@router.message(ButtonFilter(Buttons.MY_ID), ClientState.main_menu)
async def my_id(message: Message):
    await message.answer(
        f"Ваш ID: {message.from_user.id}", reply_markup=main_menu_client_keyboard
    )
    logger.info(f"To user {message.from_user.id} sent the ID")


@router.message(Command("oferta"))
async def send_offer_agreement(
    message: Message, bot: Bot, state: FSMContext, redis: Redis
):
    await set_state_with_redis(state, redis, message, ClientState.main_menu)

    await bot.send_chat_action(chat_id=message.chat.id, action="upload_document")

    file_to_send = FSInputFile(
        settings.bot.path_to_files / "oferta_dogovor.pdf", filename="Договор оферты.pdf"
    )

    await message.answer_document(
        document=file_to_send,
        caption="Используя бота, Вы автоматически принимаете условия оферты",
        reply_markup=main_menu_client_keyboard,
    )

    logger.info(f"To user {message.from_user.id} sent the oferta")


@router.message(ButtonFilter(Buttons.REFERAL_LINK), ClientState.main_menu)
async def referal_link(message: Message):
    await message.answer(
        f"Ваша реферальная ссылка: `t.me/{settings.bot.username}?start={message.from_user.id}`",
        reply_markup=main_menu_client_keyboard,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    logger.info(f"To user {message.from_user.id} sent the referal link")


@router.message(ButtonFilter(Buttons.MAIN_MENU))
async def main_menu(message: Message, state: FSMContext, redis: Redis):
    await state.clear()
    await set_state_with_redis(state, redis, message, ClientState.main_menu)
    await message.answer("Главное меню", reply_markup=main_menu_client_keyboard)

    logger.info(f"To user {message.from_user.id} sent the main menu")

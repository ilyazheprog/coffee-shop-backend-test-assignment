import asyncio
from math import ceil, floor

from aiogram import Bot, F, Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis

from bot.filters.basic import ButtonFilter, PositiveIntFilter
from bot.handlers.routers import client_router
from bot.keyboards.basic import balance_keyboard, confirm_keyboard
from bot.keyboards.cqkb import create_payment_keyboard
from bot.states.states import ClientState
from modules.database.methods import create_transaction, get_user_balance
from modules.database.methods.configs import get_config_by_name
from modules.database.methods.transactions import (
    mark_transaction_as_canceled,
    transaction_is_canceled,
    transaction_is_completed,
    update_transaction_signature,
)
from modules.database.methods.users import add_balance, user_is_referral
from modules.dataclasses import Buttons
from modules.dataclasses.configs import Configs
from modules.dataclasses.transaction_types import TransactionTypes
from modules.envs import settings
from modules.logs import logger
from modules.redis.main import set_state_with_redis
from modules.robokassa_api import AsyncPaymentProcessor

router = Router()
client_router.include_router(router)

flag = dict(waiting_payment=False)


@router.message(ButtonFilter(Buttons.BALANCE), or_f(ClientState.main_menu, ClientState.balance_menu))
async def balance_menu(message: Message, state: FSMContext, redis: Redis):
    balance = await get_user_balance(message.from_user.id)
    await set_state_with_redis(state, redis, message, ClientState.balance_menu)
    await message.answer(f"Ваш баланс: {balance}", reply_markup=balance_keyboard)
    logger.info(f"User {message.from_user.id} accessed balance menu. Balance: {balance}")


@router.message(ButtonFilter(Buttons.ADD_FUNDS), ClientState.balance_menu)
async def add_funds(message: Message, state: FSMContext, redis: Redis):
    if (
        await get_config_by_name(Configs.RECEIVE_PAYMENT)
    ).value == Configs.RECEIVE_PAYMENT_FALSE:
        await message.answer("Пополнение временно недоступно.")
        logger.warning(
            f"User {message.from_user.id} tried to add funds, but the payment is locked."
        )
        return
    await set_state_with_redis(state, redis, message, ClientState.add_funds)
    await message.answer("Введите сумму пополнения")
    logger.info(f"User {message.from_user.id} started funds addition process.")


@router.message(PositiveIntFilter(), ClientState.add_funds)
async def enter_num(message: Message, state: FSMContext, redis: Redis):
    amount = int(message.text)
    await state.update_data({"num": amount})
    await set_state_with_redis(state, redis, message, ClientState.enter_amount)
    await message.answer("Подтвердить пополнение?", reply_markup=confirm_keyboard)
    logger.info(f"User {message.from_user.id} entered the amount: {amount}")


@router.message(ButtonFilter(Buttons.CORRECT), ClientState.enter_amount)
async def get_key(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis: Redis,
    payment_processor: AsyncPaymentProcessor,
):
    data = await state.get_data()
    await set_state_with_redis(state, redis, message, ClientState.wait_payment)
    _sum = data["num"]

    final_sum = (
        _sum * (1 + settings.percent.commission / 100) * (1 + settings.percent.tax / 100)
    )

    refer_sum = 0

    if refer_id := await user_is_referral(message.from_user.id):
        final_sum *= 1 + settings.percent.referral / 100
        refer_sum = _sum * settings.percent.referral / 100
        logger.info(f"User {message.from_user.id} has a referral: {refer_id}")

    final_sum = ceil(final_sum * 100) / 100
    refer_sum = floor(refer_sum * 100) / 100

    transaction_id = await create_transaction(
        user_id=message.from_user.id,
        amount=final_sum,
        transaction_type_id=TransactionTypes.ADD_FUNDS_ID,
    )

    logger.info(
        f"Transaction created for user {message.from_user.id}: Transaction ID: {transaction_id}"
    )

    sign = await payment_processor.calculate_signature(
        cost=final_sum,
        invid=transaction_id,
    )

    payment_link = await payment_processor.generate_payment_link(
        cost=final_sum,
        number=transaction_id,
        description="Пополнение баланса",
        signature=sign,
        is_test=int(settings.is_test),
    )

    try_ = 0
    sleep_time = 5
    max_tries = settings.lifetime_payment_link_minutes * 60 // sleep_time

    await update_transaction_signature(transaction_id, sign)
    paymen_msg = await message.answer(
        f"Сумма к оплате: {final_sum}\nСсылка для оплаты доступна в течение {settings.lifetime_payment_link_minutes} минут",
        reply_markup=await create_payment_keyboard(payment_link, transaction_id),
    )
    logger.info(
        f"Payment link generated for user {message.from_user.id}, Transaction ID: {transaction_id}"
    )

    global flag
    flag.update(waiting_payment=True)

    while flag.get("waiting_payment") and try_ < max_tries:
        if await transaction_is_completed(transaction_id):
            flag.update(waiting_payment=False)
            await bot.delete_message(message.chat.id, paymen_msg.message_id)

            new_sum = _sum*1.03
            if refer_id:
                new_sum += _sum*0.03

            await add_balance(message.from_user.id, new_sum)
            await bot.send_message(
                message.from_user.id, f"Баланс пополнен на сумму: {new_sum} руб.",
               reply_markup=balance_keyboard
            )
            await set_state_with_redis(state, redis, message, ClientState.balance_menu)

            logger.info(
                f"Payment completed for user {message.from_user.id}, Transaction ID: {transaction_id}"
            )
            if refer_id:
                logger.info(
                    f"User {message.from_user.id} has a referral: {refer_id}. Referral sum: {refer_sum}"
                )
                await add_balance(refer_id, refer_sum)
                logger.info(f"Referral sum added to user {refer_id}")
                await bot.send_message(
                    refer_id,
                    f"Ваш баланс пополнен на сумму: {refer_sum} руб. за реферала",
                )

            break
        await asyncio.sleep(sleep_time)
        try_ += 1

    if flag.get("waiting_payment"):
        flag.update(waiting_payment=False)
        await mark_transaction_as_canceled(transaction_id)
        await bot.delete_message(message.chat.id, paymen_msg.message_id)
        await bot.send_message(
            message.from_user.id, "Оплата не прошла! Время ожидания истекло.",
            reply_markup=balance_keyboard
        )
        logger.warning(
            f"Payment failed for user {message.from_user.id}, Transaction ID: {transaction_id}"
        )


@router.callback_query(F.data.startswith(Buttons.CANCEL), ClientState.wait_payment)
async def cancel_payment(query: CallbackQuery, bot: Bot, state: FSMContext, redis: Redis):
    await query.message.delete()

    transaction_id = int(query.data.split("_")[1])
    await set_state_with_redis(state, redis, query.message, ClientState.balance_menu)
    await bot.send_message(query.message.chat.id, "Оплата отменена.", reply_markup=balance_keyboard)

    global flag
    flag.update(waiting_payment=False)
    await mark_transaction_as_canceled(transaction_id)
    logger.info(f"User {query.from_user.id} canceled the payment process.")

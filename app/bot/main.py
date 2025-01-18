from asyncio import run

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from bot.utils.registry import registry
from modules.database.methods.users import get_all_users
from modules.envs.settings import settings
from modules.logs import logger
from modules.robokassa_api.async_api import AsyncPaymentProcessor


async def startup(dispatcher: Dispatcher, bot: Bot, redis: Redis):
    # Проверка состояния Redis для отладки
    keys = await redis.keys("*")
    if keys:
        print(f"🔑 Ключи в Redis: {keys}")
        for key in keys:
            value = await redis.get(key)
            print(f"{key}: {value}")
    else:
        print("📂 Redis пуст")

    logger.info("Bot started")
    # Пример отправки уведомления админу
    try:
        await bot.send_message(settings.bot.admin_id, "Бот запущен")
    except TelegramForbiddenError:
        logger.error(
            "Failed to send startup message to admin. Admin might have blocked the bot."
        )


class CustomKeyBuilder:
    def build(self, key, data_type):
        """
        Формируем ключ FSM, включающий имя состояния, если оно есть.
        """
        chat_id, user_id = key.chat_id, key.user_id
        state = key.state if hasattr(key, "state") and key.state else "no_state"
        return f"fsm:{chat_id}:{user_id}:{data_type}:{state}"


async def start(bot: Bot, dp: Dispatcher, redis: Redis):
    try:
        # Пример API робокассы
        payment_processor = AsyncPaymentProcessor(
            merchant_login=settings.robokassa.merchant_login,
            merchant_password_1=settings.robokassa.merchant_password_1,
            merchant_password_2=settings.robokassa.merchant_password_2,
        )

        # Регистрируем `startup` с замыканием
        async def startup_wrapper(dispatcher: Dispatcher):
            await startup(dispatcher, bot, redis)

        dp.startup.register(startup_wrapper)

        # Передача хранилища в диспетчер
        await dp.start_polling(bot, payment_processor=payment_processor, redis=redis)
    finally:
        await bot.session.close()
        logger.info("Bot stopped")
        await redis.close()  # Закрытие подключения к Redis


def main():
    # Инициализация Redis и FSM Storage
    redis = Redis(host="redis", port=6379)
    storage = RedisStorage(redis, key_builder=CustomKeyBuilder())
    dp = Dispatcher(storage=storage)

    # Регистрация модулей бота
    registry(dp)

    run(start(settings.bot.bot, dp, redis))


if __name__ == "__main__":
    main()

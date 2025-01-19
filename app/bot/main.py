from asyncio import run

from aiogram import Bot, Dispatcher

from bot.utils.registry import registry
from modules.envs.settings import settings


async def startup(dispatcher: Dispatcher, bot: Bot):
    await bot.send_message(settings.bot.admin_id, "Бот запущен")


async def start(bot: Bot, dp: Dispatcher):
    try:

        async def startup_wrapper(dispatcher: Dispatcher):
            await startup(dispatcher, bot)

        dp.startup.register(startup_wrapper)

        await dp.start_polling(bot)
    finally:
        await bot.session.close()


def main():
    dp = Dispatcher()

    registry(dp)

    run(start(settings.bot.bot, dp))


if __name__ == "__main__":
    main()

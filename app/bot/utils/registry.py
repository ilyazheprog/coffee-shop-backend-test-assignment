from aiogram import Dispatcher

from bot.handlers.routers import admin_router, barista_router, client_router


def registry_middlewares(dp: Dispatcher):
    pass


def registry_handlers(dp: Dispatcher):
    dp.include_router(admin_router)
    dp.include_router(barista_router)
    dp.include_router(client_router)


def registry(dp: Dispatcher):
    registry_middlewares(dp)
    registry_handlers(dp)

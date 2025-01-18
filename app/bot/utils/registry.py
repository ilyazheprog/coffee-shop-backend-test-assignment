from aiogram import Dispatcher


def registry_middlewares(dp: Dispatcher):
    pass


def registry_handlers(dp: Dispatcher):
    pass

def registry(dp: Dispatcher):
    registry_middlewares(dp)
    registry_handlers(dp)

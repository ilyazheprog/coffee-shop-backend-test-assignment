from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from modules.dataclasses.buttons import Buttons

client_main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=Buttons.MENU),
            KeyboardButton(text=Buttons.ORDERS),
            KeyboardButton(text=Buttons.MAKE_ORDER),
        ],
    ],
    resize_keyboard=True,
)

barista_and_admin_main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=Buttons.MENU),
            KeyboardButton(text=Buttons.ORDERS),
        ],
    ],
    resize_keyboard=True,
)

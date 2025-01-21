from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from modules.dataclasses.buttons import Buttons


def generate_categories_keyboard(categories):
    keyboard = []
    btns_in_row = 2
    row = []
    for i, category in enumerate(categories):
        button = InlineKeyboardButton(
            text=category["name"], callback_data=f"select_category:{category['id']}"
        )
        row.append(button)
        if (i + 1) % btns_in_row == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append(
        [
            InlineKeyboardButton(
                text=Buttons.CONFIRM_ORDER, callback_data="confirm_order"
            )
        ]
    )

    keyboard.append(
        [InlineKeyboardButton(text=Buttons.CANCEL, callback_data="cancel_order")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def generate_menu_keyboard(menu_items):
    keyboard = []
    for item in menu_items:
        button = InlineKeyboardButton(
            text=f"{item['name']} - {item['price']} руб.",
            callback_data=f"select_item:{item['id']}",
        )
        keyboard.append([button])
    keyboard.append(
        [
            InlineKeyboardButton(
                text=Buttons.CONFIRM_ORDER, callback_data="confirm_order"
            )
        ]
    )
    keyboard.append(
        [InlineKeyboardButton(text=Buttons.CANCEL, callback_data="cancel_order")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def generate_quantity_keyboard(item_id, quantity):
    keyboard = [
        [
            InlineKeyboardButton(
                text="-", callback_data=f"decrease_quantity:{item_id}"
            ),
            InlineKeyboardButton(text=str(quantity), callback_data="noop"),
            InlineKeyboardButton(
                text="+", callback_data=f"increase_quantity:{item_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text=Buttons.CONFIRM, callback_data=f"confirm_quantity:{item_id}"
            ),
            InlineKeyboardButton(text=Buttons.CANCEL, callback_data="cancel_order"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def generate_delivery_methods_keyboard(delivery_methods):
    keyboard = []
    for method in delivery_methods:
        button = InlineKeyboardButton(
            text=method["name"], callback_data=f"select_delivery_method:{method['id']}"
        )
        keyboard.append([button])
    keyboard.append(
        [InlineKeyboardButton(text=Buttons.CANCEL, callback_data="cancel_order")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


confirm_order_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=Buttons.CONFIRM_ORDER, callback_data="confirm_order"
            ),
            InlineKeyboardButton(
                text=Buttons.CANCEL_ORDER, callback_data="cancel_order"
            ),
        ]
    ]
)

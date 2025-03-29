from aiogram import types

from components.templates import KEYBOARD_MESSAGES


main_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text=KEYBOARD_MESSAGES[0])],
        [
            types.KeyboardButton(text=KEYBOARD_MESSAGES[1]),
            types.KeyboardButton(text=KEYBOARD_MESSAGES[2]),
        ],
    ],
    resize_keyboard=True,
)

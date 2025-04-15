from aiogram import types

from admin.templates import ADMIN_KEYBOARD_MESSAGE


admin_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text=ADMIN_KEYBOARD_MESSAGE[0]),
            types.KeyboardButton(text=ADMIN_KEYBOARD_MESSAGE[1]),
        ],
        [
            types.KeyboardButton(text="🔄 Обновить бота"),
        ]
    ],
    resize_keyboard=True,
)


admin_confirm_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text="✅ Да"),
            types.KeyboardButton(text="❌ Отмена"),
        ]
    ],
    resize_keyboard=True,
)

import logging
import sys
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext


from configs import BOT_TOKEN, ADMIN_USER_ID
from components import templates
from keyboards.main_keyboard import main_keyboard
from handlers import menu_handlers, state_handlers
from admin.state import AdminLoginState

from admin.keyboard import admin_keyboard
from admin.handlers import admin_router

from filters.filters import MainFilter
from db import query


dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    if message.from_user.id == query.get_admin_id():
        return await message.answer(
            "Добро пожаловать! Выберите действия: ", reply_markup=admin_keyboard
        )

    await message.answer(templates.START_MESSAGE, reply_markup=main_keyboard)


@dp.message(Command("admin"))
async def admin(message: types.Message, state: FSMContext):
    await state.set_state(AdminLoginState.login)
    await message.answer("Введите логин: ")


@dp.message(Command("get_image_id_mozgi_ne_ebi"))
async def get_file_id(message: types.Message):
    file_id = message.video.file_id
    await message.answer(file_id)


async def main():
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_routers(
        admin_router, menu_handlers.menu_router, state_handlers.state_router
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        ...

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from filters.filters import MainFilter
from components import templates
from components import templates, html_templates
from components.validations import is_valid_message
from keyboards.main_keyboard import main_keyboard
from admin.keyboard import admin_keyboard

from handlers.state_handlers import state_router

from states.state import GetInvoiceNumberState, ReadyGoodsState

from db import query


menu_router = Router()


@menu_router.message(MainFilter(templates.KEYBOARD_MESSAGES[0]))
async def info(message: Message):
    await message.answer(html_templates.DESCRIPTION_MESSAGE)
    await message.answer_video(templates.VIDEO_FILE_ID)


@menu_router.message(MainFilter(templates.KEYBOARD_MESSAGES[1]))
async def get_commodity(message: Message, state: FSMContext):
    await message.answer(templates.GET_COMMODITY_MESSAGE)
    await state.set_state(GetInvoiceNumberState.invoice_number)


@menu_router.message(MainFilter(templates.KEYBOARD_MESSAGES[2]))
async def issue_info_goods(message: Message, state: FSMContext):
    await message.answer(templates.GET_CLIENT_CODE_MESSAGE)
    await state.set_state(ReadyGoodsState.client_code)


@state_router.message()
async def handle_invalid_message(message: Message):
    if not is_valid_message(message.text):
        if message.from_user.id != query.get_admin_id():
            await message.delete()
            await message.answer(templates.IS_VALID_MESSAGE, reply_markup=main_keyboard)
        else:
            await message.delete()
            await message.answer(
                templates.IS_VALID_MESSAGE, reply_markup=admin_keyboard
            )

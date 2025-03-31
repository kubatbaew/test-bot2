from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from admin.state import AdminLoginState, GiveGoodState
from configs import ADMIN_LOGIN, ADMIN_PASSWORD
from filters.filters import MainFilter

from admin.keyboard import admin_keyboard, admin_confirm_keyboard
from admin.templates import ADMIN_KEYBOARD_MESSAGE
from keyboards.main_keyboard import main_keyboard
from components.html_templates import get_goods_client_for_admin

from components import templates

from db import query
from logic.get_client_goods import get_goods, get_user_data, update_checked_status


admin_router = Router()


@admin_router.message(AdminLoginState.login)
async def admin_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await state.set_state(AdminLoginState.password)
    await message.answer("Введите пароль: ")


@admin_router.message(AdminLoginState.password)
async def password_admin(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)

    user_data = await state.get_data()

    if user_data["login"] == ADMIN_LOGIN and user_data["password"] == ADMIN_PASSWORD:
        await state.clear()

        query.update_admin_id(new_id=message.from_user.id)

        await message.answer(
            "Добро пожаловать! Выберите действия: ", reply_markup=admin_keyboard
        )
    else:
        await state.clear()
        await message.answer("Извините! Попробуйте ещё раз")


@admin_router.message(MainFilter(ADMIN_KEYBOARD_MESSAGE[0]))
async def give_goods(message: types.Message, state: FSMContext):
    await state.set_state(GiveGoodState.client_code)
    await message.answer(templates.ADMIN_GET_CLIENT_CODE_MESSAGE)


@admin_router.message(GiveGoodState.client_code)
async def get_name(message: types.Message, state: FSMContext):
    client_code = message.text[:2].upper() + message.text[2:]
    await state.update_data(client_code=client_code)
    data = await state.get_data()

    # await state.clear()

    wait = await message.answer("Ждите...")

    goods_data = get_goods(data["client_code"], "ADMIN", admin=True)
    await wait.delete()

    if not goods_data["goods"]:
        await message.answer(
            "Товара пока нет."
        )
    else:
        content = await get_goods_client_for_admin(goods_data)
        await state.set_state(GiveGoodState.confirm)

        await message.answer(content)
        await message.answer("⚠️ Вы уверены, что хотите выдать товар?", reply_markup=admin_confirm_keyboard)


@admin_router.message(GiveGoodState.confirm)
async def update_data(message: types.Message, state: FSMContext):
    data = await state.get_data()
    kk = data["client_code"]
    if message.text == "✅ Да":

        del_mes = await message.answer("Ждите, идет обновление ⏳")

        upd = update_checked_status(kk)
        if upd:
            await del_mes.delete()
            await state.clear()
            await message.answer("Вы успешно выдали товары! ✅", reply_markup=admin_keyboard)
        else:
            await state.clear()
            await message.answer("Произошла ошибка! ❌", reply_markup=admin_keyboard)
    else:
        await state.clear()
        await message.answer("Вы отменили выдачу товаров! ❌", reply_markup=admin_keyboard)




@admin_router.message(MainFilter(ADMIN_KEYBOARD_MESSAGE[1]))
async def logout_admin(message: types.Message):
    query.clear_admin_id()

    await message.answer("Удачного вам дня!", reply_markup=main_keyboard)

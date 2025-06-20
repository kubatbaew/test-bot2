import asyncio

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.state import GetInvoiceNumberState, ReadyGoodsState
from logic.get_cargo_data import get_data
from components.templates import (
    NO_CORRECT_INVOICE_MESSAGE,
    VIDEO_FILE_ID,
    GET_NAME_MESSAGE,
    GET_PHONE_NUMBER_MESSAGE,
)

from components import html_templates
from components.html_templates import (
    get_send_data_message,
    get_goods_client,
    ISSUE_INFO_NEXT_MESSAGE,
)
from keyboards.main_keyboard import main_keyboard

from logic.get_client_goods import get_goods, get_goods_next, get_user_data

import logging

logging.basicConfig(level=logging.INFO)

state_router = Router()


@state_router.message(GetInvoiceNumberState.invoice_number)
async def response_invoice(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(html_templates.UPDATE_TEXT_BOT)
    loading_message = await message.answer(text="Ваш запрос принят⏳")

    try:
        data = await get_data(message.text)
        await loading_message.delete()

        if data["data"]["data"]["wlOrder"] is None:
            await message.answer(NO_CORRECT_INVOICE_MESSAGE, reply_markup=main_keyboard)
            await message.answer_video(VIDEO_FILE_ID)
            return

        content = await get_send_data_message(data)

        await message.answer(content, reply_markup=main_keyboard)
        await message.answer(html_templates.UPDATE_TEXT_BOT)
    except Exception as e:
        await message.answer(
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже. dev={}".format(
                e
            )
        )
        await message.answer(html_templates.UPDATE_TEXT_BOT)


@state_router.message(ReadyGoodsState.client_code)
async def get_client_code(message: Message, state: FSMContext):
    if 'kk' not in message.text.lower() and "кк" not in message.text.lower():
        await message.answer(
            "Пожалуйста введите полный клиентский код «Пример: KK-ваш код»",
        )
        await state.set_state(ReadyGoodsState.client_code)
        return

    client_code = message.text[:2].upper() + message.text[2:]
    await state.update_data(client_code=client_code)
    await state.set_state(ReadyGoodsState.name)
    await message.answer(html_templates.UPDATE_TEXT_BOT)
    await message.answer(GET_NAME_MESSAGE)
    


@state_router.message(ReadyGoodsState.name)
async def send_client_code(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(html_templates.UPDATE_TEXT_BOT)
    wait_mes = await message.answer("Подождите, идёт поиск... 🔍⏳")
    data = await state.get_data()
    # await state.clear()
    # await state.set_state(None)

    # print(data)

    print(data)

    kk_code = data["client_code"] if "KK" in data["client_code"] else data["client_code"].replace("КК", "KK")
    kk_name_db = get_user_data(kk_code)

    logging.info("***")
    logging.info(data["name"])
    logging.info(kk_name_db)

    kk_parts = kk_name_db[1].strip().lower().split()
    data_name_parts = data["name"].strip().lower().split()
    logging.info(f"Names = {kk_parts} - {data_name_parts}")
    
    if kk_name_db[0] != kk_code:
        await message.answer(
            "Вы неправильно ввели свой клиентский код (пример - ваш код: KK-ваш код)",
            reply_markup=main_keyboard,
        )
        await state.clear()
        await wait_mes.delete()
        return

    elif not any(part in kk_parts for part in data_name_parts if part != "n"):
        logging.info(f"dont' correct name = {kk_parts} - {data_name_parts}")
        await message.answer(
            "❗ Похоже, вы ввели некорректное имя. Пожалуйста, попробуйте снова.",
        )
        await state.set_state(ReadyGoodsState.name)
        await wait_mes.delete()
        return 

    goods_data = get_goods(kk_code, data["name"], False)
    next_goods_data = get_goods_next(kk_code, data["name"], False)

    await wait_mes.delete()

    # Проверка на корректность имени
    if not goods_data["name_valid"] or not next_goods_data["name_valid"]:
        await message.answer(
            "❗ Похоже, вы ввели некорректное имя. Пожалуйста, попробуйте снова.",
        )
        await state.set_state(ReadyGoodsState.name)
        return

    # Объединяем товары
    combined_goods = (goods_data.get("client_data", {}).get("goods", []) +
                    next_goods_data.get("client_data", {}).get("goods", []))
    
    logging.info(combined_goods)
    # Если товаров нет вообще
    if not combined_goods:
        await message.answer(html_templates.UPDATE_TEXT_BOT)
        await message.answer(
            "Товара пока нет. Вы можете узнать его местоположение, нажав на кнопку ниже: 📦 Отследить посылку",
            reply_markup=main_keyboard,
        )
        return

    # Берем данные клиента из одного из источников (предпочтительно из основного)
    client_data = goods_data.get("client_data") or next_goods_data.get("client_data")
    client_data["goods"] = combined_goods
    logging.info(client_data)

    # Проверка имени
    if not client_data.get("name"):
        await message.answer(html_templates.UPDATE_TEXT_BOT)
        await message.answer("Пожалуйста попробуйте по позже", reply_markup=main_keyboard)
        return

    # Отправка информации
    await message.answer(html_templates.UPDATE_TEXT_BOT)
    content = await get_goods_client({"client_data": client_data})
    await message.answer(content)
    await message.answer(ISSUE_INFO_NEXT_MESSAGE, reply_markup=main_keyboard)

    await state.clear()

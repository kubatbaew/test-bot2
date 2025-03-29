from aiogram.fsm.state import StatesGroup, State


class GetInvoiceNumberState(StatesGroup):
    invoice_number = State()


class ReadyGoodsState(StatesGroup):
    client_code = State()
    name = State()
    phone_number = State()

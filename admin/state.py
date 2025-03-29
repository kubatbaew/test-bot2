from aiogram.fsm.state import StatesGroup, State


class AdminLoginState(StatesGroup):
    login = State()
    password = State()


class GiveGoodState(StatesGroup):
    client_code = State()
    name = State()
    phone_number = State()
    confirm = State()
    

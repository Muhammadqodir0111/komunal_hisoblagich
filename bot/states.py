from aiogram.fsm.state import State, StatesGroup


class ReadingStates(StatesGroup):
    waiting_account_number = State()
    choosing_meter = State()
    waiting_value = State()
    waiting_photo = State()
    confirming = State()


class RejectStates(StatesGroup):
    waiting_reason = State()
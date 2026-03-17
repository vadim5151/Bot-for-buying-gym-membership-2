from aiogram.fsm.state import StatesGroup, State



class Data(StatesGroup):
    quarter = State()
    month_and_year=State()
    year=State()
    custom_period = State()
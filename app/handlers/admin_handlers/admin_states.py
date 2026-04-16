from aiogram.fsm.state import StatesGroup, State



class StatisticData(StatesGroup):
    quarter = State()
    month_and_year=State()
    year=State()
    custom_period = State()


class PriceEditData(StatesGroup):
    pass
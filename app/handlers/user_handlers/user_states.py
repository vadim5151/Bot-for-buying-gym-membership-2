from aiogram.fsm.state import StatesGroup, State



class ChangeProfile(StatesGroup):
    name = State()
    birthday = State()


class Registration(StatesGroup):
    name = State()
    birthdate = State()


class BuyMembership(StatesGroup):
    selecting_month = State()
    confirming = State()


class NotificationSettings(StatesGroup):
    choosing_days = State()
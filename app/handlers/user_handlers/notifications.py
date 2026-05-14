from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from database.repository import UserRepository, PriceRepository, NotificationRepository
from app.messages import User



router = Router()

user_repo = UserRepository()
price_repo = PriceRepository()
notification_repo = NotificationRepository()


@router.message(F.text == 'Настройка уведомлений')
async def setting_notifications_payments(message: Message):
    await message.delete()

    available_notificatons = await notification_repo.find_one()
    available_notificatons = available_notificatons['available_periods']

    user_periods = await user_repo.find_one_by_id(message.from_user.id)
    user_periods = user_periods['notification_days_period']

    await message.answer(User.NOTIFICATION_SETTINGS, reply_markup=kb.setting_notifications_payment_kb(available_notificatons, user_periods))


@router.callback_query(F.data.startswith('toggle_'))
async def process_toggle(callback: CallbackQuery):
    days = int(callback.data[7:])
    user_periods = await user_repo.find_one_by_id(callback.from_user.id)
    user_periods = user_periods['notification_days_period']

    if days in user_periods:
        action = 'pull'
    else:
        action = 'push'

    await user_repo.update_notification(callback.from_user.id, action, days)

    available_notificatons = await notification_repo.find_one()
    available_notificatons = available_notificatons['available_periods']

    user_periods = await user_repo.find_one_by_id(callback.from_user.id)
    user_periods = user_periods['notification_days_period']

    await callback.message.edit_text(User.NOTIFICATION_SETTINGS, reply_markup=kb.setting_notifications_payment_kb(available_notificatons, user_periods))

    await callback.answer()












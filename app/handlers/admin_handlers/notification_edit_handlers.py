import asyncio 

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext

from init import bot
import app.keyboards as kb
from database.repository import NotificationRepository
from app.messages import AdminNotification
from app.handlers.admin_handlers.admin_states import NotitficationData



router = Router()
notification_repo = NotificationRepository()

@router.message(F.text == 'Редактирование уведомлений ✏️')
async def editing_notification(message: Message):
    await message.delete()
    await message.answer(AdminNotification.NOTIFICATION_SETTINGS, reply_markup=kb.notification_edit_btn)
    

@router.callback_query(F.data == 'automatically')
async def adding_automatically(callback: CallbackQuery):
    await notification_repo.insert_one([1, 3, 7])
    await callback.message.edit_text(AdminNotification.PERIODS_ADDED_AUTOMATICALLY)
    await callback.answer()


@router.callback_query(F.data == 'manually')
async def adding_manually(callback: CallbackQuery, state: FSMContext):
    await state.set_state(NotitficationData.days)
    await callback.message.edit_text(AdminNotification.ASK_PERIODS_ADDED_MANUALLY)
    await callback.answer()


@router.message(NotitficationData.days)
async def adding_manually(message: Message, state: FSMContext):
    await message.delete()
    days_msg = message.text.split(' ')
    days = [int(day) for day in days_msg]
    try:
        available_notificatons = await notification_repo.find_one()
        available_notificatons = available_notificatons['notification_days_period']
        for day in days:
            if day in available_notificatons:
                await message.answer('Такой период уже существует')
            else:
                await notification_repo.add_notification_days_period(day)
                await message.answer(AdminNotification.PERIODS_ADDED_MANUALLY)
    except:
        await notification_repo.insert_one(days)
        await message.answer(AdminNotification.PERIODS_ADDED_MANUALLY)
    await state.clear()


@router.callback_query(F.data == 'delete_periods')
async def delete_period(callback: CallbackQuery):
    try:
        available_notificatons = await notification_repo.find_one()
        available_notificatons = available_notificatons['notification_days_period']
        await notification_repo.delete_periods()
        await callback.message.edit_text('Периоды успешно удалены 🗑️')
    except:
        await callback.message.edit_text('Периодов для удаления нет ❌')
    await callback.answer()


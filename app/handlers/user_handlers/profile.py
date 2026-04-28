from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from init import bot
import app.keyboards as kb
from database.repository import UserRepository, PriceRepository, NotificationRepository, PurchasesRepository, TempMessageRepository
from app.messages import User
from app.handlers.user_handlers.user_states import ChangeProfile
from validators import validate_full_name, validate_birthdate
from exceptions import InvalidFullName, InvalidFullNameWordCounts, FutureBirthDate, AgeLimit, InvalidDateFormat



router = Router()

user_repo = UserRepository()
price_repo = PriceRepository()
notification_repo = NotificationRepository()
purchase_repo = PurchasesRepository()
temp_message_repo = TempMessageRepository()


@router.message(F.text == "Мой профиль")
async def show_profile(message: Message):
    await message.delete()

    tg_id = message.from_user.id
    user = await user_repo.find_one_by_id(tg_id)
    if not user:
        await message.answer("Сначала зарегистрируйтесь через /start")
        return
    
    # Последняя активная покупка (по дате окончания)
    purchases = await purchase_repo.get_by_user_id(tg_id)

    active_purchase = None
    now = datetime.now()

    for purchase in purchases:
        if purchase["expiration_date"] > now:
            active_purchase = purchase
            break
    
    text = f"👤 <b>Ваш профиль</b>\n\n"
    text += f"<b>ФИО</b>: {user.get('full_name')}\n"
    text += f"<b>Дата рождения</b>: {user.get('date_of_birth').strftime('%d.%m.%Y')}\n"
    
    if active_purchase:
        until = active_purchase["expiration_date"]
        days_left = (until - now).days
        text += f"🎟 <b>Абонемент активен до</b> {until.strftime('%d.%m.%Y')} (осталось {days_left} дн.)\n"

    else:
        text += "❌ <b>Нет активного абонемента</b>.\n"
    
    await message.answer(text, reply_markup=kb.change_registration)


@router.callback_query(F.data == 'change_fio')
async def change_fio(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeProfile.name)

    temp_message = await callback.message.edit_text(User.ASK_FULLNAME)

    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)


@router.message(ChangeProfile.name)
async def change_fio(message: Message, state: FSMContext):
    await message.delete()

    full_name = message.text
    try:
        validate_full_name(full_name)
    except InvalidFullName:
        temp_message = await message.answer('Имя должно начинаться с заглавных букв и состоять только из букв')
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
        return
    except InvalidFullNameWordCounts:
        temp_message = await message.answer('Длина имени не соответствует')
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
        return
    await temp_message_repo.delete_temp_messages(message.from_user.id, message.chat.id, bot)
    await user_repo.update_fio(message.from_user.id, full_name)

    await message.answer('✅ Имя измененно')
    await state.clear()


@router.callback_query(F.data == 'change_date_of_birth')
async def change_date_of_birth(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeProfile.birthday)
    temp_message = await callback.message.edit_text(User.ASK_BIRTHDATE)
    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)


@router.message(ChangeProfile.birthday)
async def change_date_of_birth(message: Message, state: FSMContext):
    await message.delete()
    date_str = message.text.strip()
    try:
        validate_birthdate(date_str)
    except InvalidDateFormat:
        temp_message = await message.answer('Неправильный формат')
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
        return
    except FutureBirthDate:
        temp_message = await message.answer('Возраст слишком маленький')
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
        return
    except AgeLimit:
        temp_message = await message.answer('Возраст слишком большой')
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
        return

    await temp_message_repo.delete_temp_messages(message.from_user.id, message.chat.id, bot)
    await user_repo.update_date_of_birth(message.from_user.id, datetime.strptime(date_str,'%d.%m.%Y'))
    await message.answer('✅ Дата рождения измененна')
    await state.clear()



   
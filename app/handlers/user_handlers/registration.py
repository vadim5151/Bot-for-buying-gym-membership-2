from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from init import bot
import app.keyboards as kb
from database.repository import UserRepository, TempMessageRepository
from app.messages import User
from app.handlers.user_handlers.user_states import Registration
from validators import validate_full_name, validate_birthdate
from app.messages import User



router = Router()

user_repo = UserRepository()
temp_message_repo = TempMessageRepository()



@router.message(Registration.name)
async def get_username(message: Message, state: FSMContext):
    await message.delete()

    full_name = message.text
    is_valid, error = validate_full_name(full_name)
    if not is_valid:
        temp_message = await message.answer(error)
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)

        return
    
    await state.update_data(full_name=full_name)

    await state.set_state(Registration.birthdate)

    await message.answer(User.ASK_BIRTHDATE)


@router.message(Registration.birthdate)
async def get_date_of_birth(message: Message, state: FSMContext):
    await message.delete()

    date_str = message.text.strip()
    is_valid, date_birth = validate_birthdate(date_str)
    if not is_valid:
        temp_message = await message.answer(date_birth) 
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)

        return
    
    data = await state.get_data()
    full_name = data["full_name"]
    tg_id = message.from_user.id

    user = {
            'tg_id': tg_id, 
            'full_name': full_name,           
            'date_of_birth': date_birth.strftime('%d.%m.%Y'),
            'is_admin': False ,
            'notification_days_period': [], 
        }

    await user_repo.insert_one(user)
    await state.clear()

    await temp_message_repo.clear_temp_message_ids(tg_id, message.chat.id, bot)
    
    await message.answer(f"✅ Регистрация завершена!\n\n"
                f"📋 Ваши данные:\n"
                f"• ФИО: {full_name}\n"
                f"• Дата рождения:  {date_birth.strftime('%d.%m.%Y')}\n", reply_markup=kb.get_main_menu_keyboards(False))


    
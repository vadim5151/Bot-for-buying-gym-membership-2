from datetime import datetime
import traceback

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
from exceptions import InvalidFullName, InvalidFullNameWordCounts, AgeLimit, FutureBirthDate



router = Router()

user_repo = UserRepository()
temp_message_repo = TempMessageRepository()



@router.message(Registration.name)
async def get_username(message: Message, state: FSMContext):
    await message.delete()

    try:
        full_name = message.text

        validate_full_name(full_name)
        await state.update_data(full_name=full_name)
        await state.set_state(Registration.birthdate)
        message_text = User.ASK_BIRTHDATE

    except InvalidFullName:
        message_text = User.INVALID_FULLNAME

    except InvalidFullNameWordCounts:
        message_text = User.INVALID_FULLNAME_WORD_COUNTS
    
    except Exception as e:
        print(f'Error {e}')
        message_text = User.UNEXPECTED_ERROR


    await message.answer(message_text)
    


@router.message(Registration.birthdate)
async def get_date_of_birth(message: Message, state: FSMContext):
    await message.delete()

    date_str = message.text

    try:
        validate_birthdate(date_str)
        await state.update_data(birthday=date_str)
        await register(message, state)

        return
    except FutureBirthDate:
        message_text = User.FUTURE_BIRTHDATE
    
    except AgeLimit:
        message_text = User.AGE_TOO_HIGH
    
    except Exception as e:
        print(f'Error {e}')
        message_text = User.UNEXPECTED_ERROR

    await message.answer(message_text)


async def register(message: Message, state: FSMContext):

    data = await state.get_data()
    full_name = data["full_name"]
    birthdate = data['birthday']
    tg_id = message.from_user.id

    user = {
            'tg_id': tg_id, 
            'full_name': full_name,           
            'date_of_birth': datetime.strptime(birthdate, '%d.%m.%Y'),
            'is_admin': False,
            'notification_days_period': [], 
        }

    await user_repo.insert_one(user)
    await state.clear()

    await temp_message_repo.clear_temp_message_ids(tg_id, message.chat.id, bot)
    
    await message.answer(f"✅ Регистрация завершена!\n\n"
                f"📋 Ваши данные:\n"
                f"• ФИО: {full_name}\n"
                f"• Дата рождения:  {birthdate}\n", reply_markup=kb.get_main_menu_keyboards(False))


   
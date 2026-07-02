from datetime import datetime
import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from modules.tg_bot.__init__ import bot
from database.repositories.user_repository import UserRepository
from modules.tg_bot.app.messages import User
from modules.tg_bot.app.handlers.user_handlers.user_states import Registration
from modules.tg_bot.validators import validate_full_name, validate_birthdate
from modules.tg_bot.app.messages import User
from modules.tg_bot.exceptions import (
    InvalidFullName,
    InvalidFullNameWordCounts, 
    AgeLimit, 
    FutureBirthDate
)
import modules.tg_bot.app.keyboards as kb



router = Router()
user_repo = UserRepository()

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
        logging.error(msg=f'Error {e}')
        message_text = User.UNEXPECTED_ERROR
    temp_message = await message.answer(message_text)
    await user_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
    

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
        logging.exception(msg='Ошибка при вводе даты рождения')
        message_text = User.UNEXPECTED_ERROR
    temp_message = await message.answer(message_text)
    await user_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)


async def register(message: Message, state: FSMContext):
    data = await state.get_data()
    full_name = data["full_name"]
    birthdate = data['birthday']
    tg_id = message.from_user.id
    await user_repo.update_fio(tg_id, full_name)
    await user_repo.update_date_of_birth(tg_id, datetime.strptime(birthdate, '%d.%m.%Y'))
    await user_repo.delete_temp_messages(tg_id, message.chat.id, bot) 
    await state.clear()
    await message.answer(f"✅ Регистрация завершена!\n\n"
                f"📋 Ваши данные:\n"
                f"• ФИО: {full_name}\n"
                f"• Дата рождения:  {birthdate}\n", reply_markup=kb.get_main_menu_keyboards(False))


   
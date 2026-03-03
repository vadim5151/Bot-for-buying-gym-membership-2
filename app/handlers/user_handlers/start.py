from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from database.repository import UserRepository, TempMessageRepository
from app.messages import User
from app.handlers.user_handlers.user_states import Registration



router = Router()

user_repo = UserRepository()
temp_message_repo = TempMessageRepository()


@router.message(Command('start'))
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.delete()

    data_user = await user_repo.find_one_by_id(message.from_user.id) 

    if data_user:
        await message.answer(User.WELCOME_BACK.format(name=data_user['full_name']), reply_markup=kb.get_main_menu_keyboards(data_user['is_admin']))
        
    else:
        await temp_message_repo.insert_one(message.from_user.id)

        temp_message = await message.answer(User.WELCOME_NEW)
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)

        temp_message = await message.answer(User.ASK_FULLNAME)

        await state.set_state(Registration.name) 
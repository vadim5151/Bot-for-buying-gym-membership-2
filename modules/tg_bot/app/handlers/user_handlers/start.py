from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.repository import UserRepository
from modules.tg_bot.app.messages import User
from modules.tg_bot.app.handlers.user_handlers.user_states import Registration
import modules.tg_bot.app.keyboards as kb



router = Router()
user_repo = UserRepository()

@router.message(Command('start'))
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.delete()
    data_user = await user_repo.find_one_by_id(message.from_user.id) 
    if data_user:
        await message.answer(User.WELCOME_BACK.format(name=data_user['full_name']), reply_markup=kb.get_main_menu_keyboards(data_user['is_admin']))
    else:
        user = {
            'tg_id': message.from_user.id, 
            'full_name': '',
            'date_of_birth': '',
            'is_admin': False,
            'notification_days_period': [],
            'temp_message_ids': [],
            'history': []
        }
        await user_repo.insert_one(user)

        temp_message = await message.answer(User.WELCOME_NEW)
        await user_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
        temp_message = await message.answer(User.ASK_FULLNAME)
        await user_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
        await state.set_state(Registration.name) 
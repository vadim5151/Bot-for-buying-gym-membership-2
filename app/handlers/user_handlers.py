import re
from datetime import datetime
import asyncio


from dateutil.relativedelta import relativedelta 
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext

from init import bot
import app.keyboards as kb
from formatters import format_price_list, format_cheque
from database.repository import UserRepository, PriceRepository, NotificationRepository, PurchasesRepository, TempMessageRepository
from app.messages import User



router = Router()

user_repo = UserRepository()
price_repo = PriceRepository()
notification_repo = NotificationRepository()
purchase_repo = PurchasesRepository()
temp_message_repo = TempMessageRepository()



def check_fio(fio: str):
    parts = fio.strip().split()
    if len(parts) not in [2, 3]:
        return False
    
    for part in parts:
        if not re.fullmatch(r'[А-ЯЁ][а-яё]{1,}(-[А-ЯЁ][а-яё]{1,})?', part):
            return False
        if len(part) < 2:  # Проверка минимальной длины
            return False
    
    return True


class Data(StatesGroup):
   month=State()
   change_fio = State()
   change_date_of_birth = State()
   waiting_confirmation = State()
   username = State()
   date_of_birth = State()
   age = State()



@router.message(Command('start'))
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.delete()
    data_user = await user_repo.find_one_by_id(message.from_user.id) 
    await temp_message_repo.insert_one(message.from_user.id)

    if data_user:
        await message.answer(User.WELCOME_BACK.format(name=data_user['user']), reply_markup=kb.get_main_menu_keyboards(data_user['is_admin']))
        
    else:
        temp_message = await message.answer(User.WELCOME_NEW)
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)

        await state.set_state(Data.username)

        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
        temp_message = await message.answer(User.ASK_FULLNAME)


@router.message(Data.username)
async def get_username(message: Message, state: FSMContext):
    await message.delete()

    if check_fio(message.text):
        await state.update_data(username=message.text)
        await state.set_state(Data.date_of_birth)

        temp_message = await message.answer(User.ASK_BIRTHDATE)

        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)

    else:
        temp_message = await message.answer(User.INVALID_FULLNAME)

        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)



@router.message(Data.date_of_birth)
async def get_date_of_birth(message: Message, state: FSMContext):
    await message.delete()

    today_date = datetime.today().date()

    try:
        birthdate = datetime.strptime(message.text, "%d.%m.%Y").date()

        if birthdate > today_date:
            temp_message = await message.answer(User.INVALID_DATE_FORMAT)

            await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)


            return None
        
        if today_date.year - birthdate.year >= 100:
            temp_message = await message.answer(User.FUTURE_BIRTHDATE)

            await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)


            return None
        
        age = today_date.year - birthdate.year
    
        if today_date.month < birthdate.month or (today_date.month == birthdate.month and today_date.day < birthdate.day):
            age -= 1

       
        
        await state.update_data(date_of_birth=birthdate)
        await state.update_data(age=age)

    except ValueError:
        temp_message = await message.answer(User.INVALID_DATE_FORMAT)

        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)


    await temp_message_repo.delete_temp_messages(message.from_user.id, message.chat.id, bot)

    data = await state.get_data()
    tg_id = message.from_user.id

    user = {
            'tg_id': tg_id, 
            'user': data['username'],           
            'date_of_birth': datetime.strftime(data['date_of_birth'],'%d.%m.%Y'),
            'is_admin': False ,
            'expiration_date': None,
            'notification_days_period': [], 
        }

    await user_repo.insert_one(user) 

    await message.answer('Добро пожаловать', reply_markup=kb.get_main_menu_keyboards(False))

    temp_message = await message.answer(f"✅ Регистрация завершена!\n\n"
                f"📋 Ваши данные:\n"
                f"• ФИО: {data['username']}\n"
                f"• Дата рождения:  {datetime.strftime(data['date_of_birth'],'%d.%m.%Y')}\n", reply_markup=kb.change_registration)

    await asyncio.sleep(15)
    await bot.delete_message(message.chat.id, temp_message.message_id)
    
    await state.clear()


@router.callback_query(F.data == 'change_fio')
async def change_fio(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Data.change_fio)

    temp_message = await callback.message.answer(User.ASK_FULLNAME)

    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)



@router.message(Data.change_fio)
async def change_fio(message: Message, state: FSMContext):
    await user_repo.update_fio(message.from_user.id, message.text)

    await temp_message_repo.delete_temp_messages(message.from_user.id, message.chat.id, bot)


    await message.delete()
    await state.clear()

    data_user = await user_repo.find_one_by_id(message.from_user.id) 

    await message.answer(f"✅ Регистрация завершена!\n\n"
                f"📋 Ваши данные:\n"
                f"• ФИО: {data_user['user']}\n"
                f"• Дата рождения:  {data_user['date_of_birth']}\n", reply_markup=kb.change_registration)


@router.callback_query(F.data == 'change_date_of_birth')
async def change_date_of_birth(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Data.change_date_of_birth)

    temp_message = await callback.message.answer(User.ASK_BIRTHDATE)

    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)



@router.message(Data.change_date_of_birth)
async def change_date_of_birth(message: Message, state: FSMContext):
    await user_repo.update_date_of_birth(message.from_user.id, message.text)
    
    await temp_message_repo.delete_temp_messages(message.from_user.id, message.chat.id, bot)


    await message.delete()
    await state.clear()

    data_user = await user_repo.find_one_by_id(message.from_user.id)

    await message.answer(f"✅ Регистрация завершена!\n\n"
                f"📋 Ваши данные:\n"
                f"• ФИО: {data_user['user']}\n"
                f"• Дата рождения:  {data_user['date_of_birth']}\n", reply_markup=kb.change_registration)


@router.message(Command('price'))
@router.message(F.text == 'Прайс')
async def get_price(message: Message):
    await message.delete()

    price_data = await price_repo.get_all_prices()

    price_list = format_price_list(price_data)
    
    months = []
    for month in price_data:
        months.append(month['month'])

    await message.answer(price_list, reply_markup=kb.create_user_btn_price_list(months))


@router.callback_query(F.data.startswith('buy_'))
async def buy_membership(callback: CallbackQuery, state: FSMContext):
    month = callback.data.split('_')[1]
    amount = await price_repo.get_by_month(int(month))
    amount = amount['price']
    today_date = datetime.today().date()

    await state.update_data(month=month)

    user_data = await user_repo.find_one_by_id(callback.from_user.id)

    if user_data['expiration_date'] != None:
        expiration_date = user_data['expiration_date']

        await callback.message.edit_text(User.HAVE_MEMBERSHIP.format(expiration_date=expiration_date), reply_markup=kb.confirmation_kb)

        await state.set_state(Data.waiting_confirmation)

    else:
        expiration_date = today_date + relativedelta(months=int(month))
        await user_repo.update_membership(callback.from_user.id, str(datetime.strftime(today_date, '%d.%m.%Y')), str(datetime.strftime(expiration_date, '%d.%m.%Y')))

        cheque = format_cheque(month, datetime.strftime(today_date, '%d.%m.%Y'), datetime.strftime(expiration_date, '%d.%m.%Y'), amount)
        await callback.message.edit_text(cheque)

        await purchase_repo.insert_purchase(int(month), amount, datetime.strftime(today_date, '%d.%m.%Y'))
        
            
    
        
    await callback.answer()

#TODO исправить название в колекции _purchase
@router.callback_query(Data.waiting_confirmation, F.data == 'confirm_purchase')
async def confirm_purchase(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    today_date = datetime.today().date()

    user_data = await user_repo.find_one_by_id(callback.from_user.id) 

    amount = await price_repo.get_by_month(int(data['month'])) 
    amount = amount['price']

    old_expiration_date = await user_repo.find_one_by_id(callback.from_user.id) 
    old_expiration_date = old_expiration_date['expiration_date']

    new_expiration_date = datetime.strptime(old_expiration_date, "%d.%m.%Y") + relativedelta(months=int(data['month']))
    await user_repo.update_membership(callback.from_user.id, str(datetime.strftime(today_date, '%d.%m.%Y')), str(datetime.strftime(new_expiration_date, '%d.%m.%Y')) )


    cheque = format_cheque(data['month'], datetime.strftime(today_date, '%d.%m.%Y'), datetime.strftime(new_expiration_date, '%d.%m.%Y'), amount)
    await callback.message.edit_text(cheque)

    await purchase_repo.insert_purchase(int(data['month']), amount, datetime.strftime(today_date, '%d.%m.%Y'))

    await state.clear()

    await callback.answer()


@router.callback_query(Data.waiting_confirmation, F.data == "cancel_purchase")
async def cancel_purchase(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(User.PURCHASE_CANCELLED)

    await state.clear()
    await callback.answer()


@router.message(F.text == 'Остатки по тарифу')
async def check_membership(message: Message):
    today_date = datetime.today()
    
    expiration_date = await user_repo.find_one_by_id(message.from_user.id)
    expiration_date = expiration_date['expiration_date']
    if expiration_date != None:
        await message.delete()
        days_left = ((datetime.strptime(expiration_date, "%d.%m.%Y"))-today_date).days
        await message.answer(User.CURRENT_MEMBERSHIP.format(expiration_date=expiration_date, days_left=days_left), reply_markup=kb.extend_membership)

    else:
        await message.answer(User.NO_MEMBERSHIP)
        await get_price(message)


@router.callback_query(F.data == 'extend_membership')
async def get_price_inline(callback: CallbackQuery):
    await get_price(callback.message)

    await callback.answer()


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
    days = callback.data[7:]
    user_periods = await user_repo.find_one_by_id(callback.from_user.id)
    user_periods = user_periods['notification_days_period']

    if int(days) in user_periods:
        await user_repo.update_notification(callback.from_user.id, 'pull', int(days))
    else:
        await user_repo.update_notification(callback.from_user.id, 'push', int(days))

    available_notificatons = await notification_repo.find_one()
    available_notificatons = available_notificatons['available_periods']

    user_periods = await user_repo.find_one_by_id(callback.from_user.id)
    user_periods = user_periods['notification_days_period']

    await callback.message.edit_text(User.NOTIFICATION_SETTINGS, reply_markup=kb.setting_notifications_payment_kb(available_notificatons, user_periods))

    await callback.answer()





import asyncio 

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext

from init import bot
from formatters import format_price_list, format_price
import app.keyboards as kb
from database.repository import PriceRepository, TempMessageRepository
from app.messages import Common, AdminPrice


router = Router()

price_repo = PriceRepository()
temp_message_repo = TempMessageRepository()



class Data(StatesGroup):
    month = State()
    amount = State()
    change_price = State()
    add_price = State()
    message_id = State()

    
@router.message(F.text == 'Редактирование прайса 🔧')
async def editing_price(message: Message):
    await message.delete()

    current_price_data = await price_repo.get_all_prices()
    current_price_list = format_price_list(current_price_data)

    months = []
    for month in current_price_data:
        months.append(month['month'])


    temp_message = await message.answer(current_price_list, reply_markup=kb.create_admin_price_list(months))
    await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
   

@router.callback_query(F.data.startswith('edit_'))
async def buy_membership(callback: CallbackQuery, state: FSMContext):
    month = callback.data.split('_')[1]

    amount = await price_repo.get_by_month(int(month))
    amount = amount['price']

    price = format_price(month, amount)

    await state.update_data(month=month, amount=amount)

    await callback.message.edit_text(f'<b>{price}</b>', reply_markup=kb.kb_edit_price_list)
    await callback.answer('')


@router.callback_query(F.data == 'remove_price')
async def remove_price(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    deleted_price = format_price(int(data['month']), int(data['amount']))
    
    await price_repo.delete_one(int(data['month']), int(data['amount']))
  
    temp_message = await callback.message.edit_text(AdminPrice.PRICE_DELETED.format(price=deleted_price))

    await asyncio.sleep(3)
    await bot.delete_message(callback.message.chat.id, temp_message.message_id)

    current_price_data = await price_repo.get_all_prices()
    current_price_list = format_price_list(current_price_data)

    months = []
    for month in current_price_data:
        months.append(month['month'])


    await callback.message.answer(current_price_list, reply_markup=kb.create_admin_price_list(months))
    await callback.answer('')

    await state.clear()


@router.callback_query(F.data == 'change_price')
async def change_price_btn(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Data.change_price)

    temp_message = await callback.message.answer(AdminPrice.ASK_NEW_PERIOD)
    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)

    
    await callback.answer('')


@router.message(Data.change_price)
async def change_price_bd(message: Message, state: FSMContext):
    if message.text and len(message.text.split()) == 2 and (message.text.split()[0].isdigit() and message.text.split()[1].isdigit()):

        data = await state.get_data()

        await price_repo.update_one(int(data['month']), int(data['amount']),
                                    int(message.text.split()[0]), int(message.text.split()[1]))
       
        
        old_price = format_price(int(data['month']), int(data['amount']))
        new_price = format_price(int(message.text.split()[0]), int(message.text.split()[1]))
        
        await message.delete()

        temp_message = await message.answer(AdminPrice.PRICE_UPDATED.format(old_price=old_price, new_price=new_price))
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)


        asyncio.sleep(3)
        await temp_message_repo.clear_temp_message_ids(message.from_user.id, message.chat.id, bot)

        current_price_data = await price_repo.get_all_prices()
        current_price_list = format_price_list(current_price_data)

        months = []
        for month in current_price_data:
            months.append(month['month'])


        temp_message = await message.answer(current_price_list, reply_markup=kb.create_admin_price_list(months))

        await state.clear()

    else:
        await message.delete()

        temp_message = await message.answer(AdminPrice.ASK_NEW_PERIOD_AGAIN)
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)



@router.callback_query(F.data == 'add_price')
async def add_price_btn(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Data.add_price)

    temp_message = await callback.message.answer(AdminPrice.ASK_NEW_PERIOD)
    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)


    await callback.answer('')


@router.message(Data.add_price)
async def add_price_db(message: Message):
    if message.text and len(message.text.split()) == 2 and (message.text.split()[0].isdigit() and message.text.split()[1].isdigit()):
        await message.delete()

        await price_repo.insert_one(int(message.text.split()[0]), int(message.text.split()[1]))
        
        price = format_price(int(message.text.split(' ')[0]), int(message.text.split(' ')[1]))

        temp_message = await message.answer(AdminPrice.PRICE_ADDED.format(price=price))

        await asyncio.sleep(3)

        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)


        await temp_message_repo.clear_temp_message_ids(message.from_user.id, message.chat.id, bot)

        current_price_data = await price_repo.get_all_prices()
        current_price_list = format_price_list(current_price_data)

        months = []
        for month in current_price_data:
            months.append(month['month'])


        temp_message = await message.answer(current_price_list, reply_markup=kb.create_admin_price_list(months))

    else:
        await message.delete()

        temp_message = await message.answer(AdminPrice.ASK_NEW_PERIOD_AGAIN)
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
       


@router.callback_query(F.data == 'cancel_edit')
async def cancel_price(callback: CallbackQuery):
    current_price_data = await price_repo.get_all_prices()

    current_price_list = format_price_list(current_price_data)

    months = []
    for month in current_price_data:
        months.append(month['month'])

    await callback.message.edit_text(current_price_list, reply_markup=kb.create_admin_price_list(months))
    await callback.answer('')



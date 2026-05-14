import asyncio 

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext

from init import bot
from formatters import generate_price_text, generate_price_text_by_month
import app.keyboards as kb
from database.repository import PriceRepository, TempMessageRepository
from app.messages import AdminPrice
from validators import validate_price_period



router = Router()

price_repo = PriceRepository()
temp_message_repo = TempMessageRepository()

class Data(StatesGroup):
    update_price = State()

    
@router.message(F.text == 'Редактирование прайса 🔧')
async def editing_price(message: Message):
    await message.delete()

    prices = await price_repo.get_all_prices()
    months = [month['month'] for month in prices]
    temp_message = await message.answer(generate_price_text(prices), reply_markup=kb.create_admin_price_list(months))
    await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
   

@router.callback_query(F.data.startswith('edit_'))
async def select_price_action(callback: CallbackQuery, state: FSMContext):
    month = callback.data.split('_')[1]
  
    amount = await price_repo.get_by_month(int(month))

    await state.update_data(month=month, amount=amount['price'])

    await callback.message.edit_text(
        f'<b>{generate_price_text_by_month(month, amount['price'])}</b>\n{AdminPrice.ASK_NEW_PERIOD}', 
        reply_markup=kb.kb_edit_price_list
    )
    await callback.answer('')


@router.callback_query(F.data == 'update_price')
async def update_price_btn(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Data.update_price)

    temp_message = await callback.message.answer(AdminPrice.ASK_NEW_PERIOD, reply_markup=kb.kb_cancel_edit)
    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)

    await callback.answer('')


@router.message(Data.update_price)
async def update_price(message: Message, state: FSMContext):
    await message.delete()

    if not validate_price_period(message.text):
        temp_message = await message.answer(AdminPrice.ASK_NEW_PERIOD_AGAIN)
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
        
        return 

    data = await state.get_data()
    month = int(message.text.split()[0])
    price = int(message.text.split()[1])

    if await price_repo.get_by_month(month):
        await price_repo.update_one(
            old_month=int(data['month']), old_amount=int(data['amount']),
            new_month=month, new_amount=price
        )
        old_price_text = generate_price_text_by_month(int(data['month']), int(data['amount']))
        new_price_text = generate_price_text_by_month(month, price)
        temp_message = await message.answer(AdminPrice.PRICE_UPDATED.format(old_price=old_price_text, new_price=new_price_text)) 
    else:
        await price_repo.insert_one(month, price)
        price_text = generate_price_text_by_month(month, price)
        temp_message = await message.answer(AdminPrice.PRICE_ADDED.format(price=price_text))

    await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
    await temp_message_repo.delete_temp_messages(message.from_user.id, message.chat.id, bot)

    current_prices = await price_repo.get_all_prices()
    current_price_text = generate_price_text(current_prices)
    months = [month['month'] for month in current_prices]

    await message.answer(current_price_text, reply_markup=kb.create_admin_price_list(months))
       

@router.callback_query(F.data == 'remove_price')
async def remove_price(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    deleted_price = generate_price_text_by_month(int(data['month']), int(data['amount']))
    await price_repo.delete_one(int(data['month']), int(data['amount']))
    temp_message = await callback.message.edit_text(AdminPrice.PRICE_DELETED.format(price=deleted_price))

    await asyncio.sleep(3)
    await bot.delete_message(callback.message.chat.id, temp_message.message_id)

    current_price_data = await price_repo.get_all_prices()
    current_price_list = generate_price_text(current_price_data)
    months = [month['month'] for month in current_price_data]

    await callback.message.answer(current_price_list, reply_markup=kb.create_admin_price_list(months))
    await callback.answer('')
    await state.clear()


@router.callback_query(F.data == 'cancel_edit')
async def cancel_price(callback: CallbackQuery, state: FSMContext):
    prices = await price_repo.get_all_prices()
    months = [month['month'] for month in prices]
    temp_message = await callback.message.edit_text(generate_price_text(prices), reply_markup=kb.create_admin_price_list(months))

    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)
    await callback.answer('Отмена')
    await state.clear()




from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from formatters import generate_price_text
from database.repository import PriceRepository, PurchasesRepository, TempMessageRepository
from app.messages import User



router = Router()

price_repo = PriceRepository()
purchase_repo = PurchasesRepository()
temp_message_repo = TempMessageRepository()


@router.message(Command('price'))
@router.message(F.text == 'Прайс')
async def get_price(message: Message):
    await message.delete()

    price_data = await price_repo.get_all_prices()

    price_list = generate_price_text(price_data)

    months = [month['month'] for month in price_data]

    await message.answer(price_list, reply_markup=kb.create_user_btn_price_list(months))


@router.callback_query(F.data.startswith('buy_'))
async def buy_membership(callback: CallbackQuery, state: FSMContext):
    today_date = datetime.now()
    purchase_data = await purchase_repo.find_one_by_id(callback.from_user.id)
    month_count = int(callback.data.split("_")[1])
    price_data = await price_repo.get_by_month(month_count)

    await state.update_data(month_count=month_count, amount=price_data["price"])

    if purchase_data and purchase_data['expiration_date']>=today_date:
        expiration_date = purchase_data['expiration_date']

        await callback.message.edit_text(
            User.HAVE_MEMBERSHIP.format(expiration_date=expiration_date.strftime('%d.%m.%Y')),
            reply_markup=kb.confirmation_kb
        )

    else:
        await callback.message.edit_text(
            User.CONFIRM_PURCHASE.format(month=month_count, price=price_data['price']), 
            reply_markup=kb.confirmation_kb
        )

    await callback.answer()


@router.callback_query(F.data == 'confirm_purchase')
async def confirm_purchase(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    purchase_data = await purchase_repo.find_one_by_id(callback.from_user.id)

    tg_id = callback.from_user.id
    month_count= data["month_count"]
    amount = data["amount"]
    
    if purchase_data:
        old_expiration_date = purchase_data['expiration_date']
        new_expiration_date = old_expiration_date + timedelta(days=30 * month_count) 

        await purchase_repo.update_membership(
            tg_id=callback.from_user.id, 
            purchase_date=datetime.now(), 
            expiration_date=new_expiration_date,
            month=month_count, 
            amount=amount
        )

        await state.clear()

        await callback.message.edit_text(
            User.BUY_MEMBERSHIP.format(expiration_date=new_expiration_date.strftime('%d.%m.%Y'))
        )

        await callback.answer()

    else:
        expiration_date = datetime.now() + timedelta(days=30 * month_count) 
    
        await purchase_repo.insert_purchase(tg_id, month_count, amount, datetime.now(), expiration_date)

        await state.clear()

        await callback.message.edit_text(
            User.BUY_MEMBERSHIP.format(expiration_date=expiration_date.strftime('%d.%m.%Y'))
        )

        await callback.answer()


@router.callback_query(F.data == "cancel_purchase")
async def cancel_purchase(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(User.PURCHASE_CANCELLED)

    await state.clear()
    await callback.answer()


@router.message(F.text == 'Остатки по тарифу')
async def check_membership(message: Message):
    today_date = datetime.today()
    
    expiration_date = await purchase_repo.find_one_by_id(message.from_user.id)
    expiration_date = expiration_date['expiration_date']

    if expiration_date:
        await message.delete()
        days_left = (expiration_date-today_date).days

        await message.answer(
            User.CURRENT_MEMBERSHIP.format(
                expiration_date=expiration_date.strftime('%d.%m.%Y'), 
                days_left=days_left
            ), 
            reply_markup=kb.extend_membership
        )

    else:
        await message.answer(User.NO_MEMBERSHIP)
        price_data = await price_repo.get_all_prices()

        price = generate_price_text(price_data)
        
        months = [month['month'] for month in price_data]

        await message.answer(price, reply_markup=kb.create_user_btn_price_list(months))


@router.callback_query(F.data == 'extend_membership')
async def get_price_inline(callback: CallbackQuery):
    price_data = await price_repo.get_all_prices()

    price_list = generate_price_text(price_data)
    
    months = [month['month'] for month in price_data]

    await callback.message.edit_text(price_list, reply_markup=kb.create_user_btn_price_list(months))

    await callback.answer()
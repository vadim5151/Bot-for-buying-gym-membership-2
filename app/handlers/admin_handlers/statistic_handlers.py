import os
from datetime import datetime as dt, timedelta

from dateutil.relativedelta import relativedelta 
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from init import bot
from formatters import generate_short_report
import app.keyboards as kb
from services.excel_reports import generate_excel_report
from database.repository import PurchasesRepository, TempMessageRepository
from app.messages import AdminStats, Common
from app.handlers.admin_handlers.admin_states import StatisticData
from utils import month_numbers, quarter_names_to_num, quarter_to_date_range
from validators import validate_month

from pprint import pprint


router = Router()

purchases_repo = PurchasesRepository()
temp_message_repo = TempMessageRepository()


@router.message(F.text == 'Статистика 📊')
async def menu_statistics(message: Message):
    await message.delete()

    await message.answer(AdminStats.MENU_TITLE, reply_markup=kb.kb_menu_statistics)


@router.callback_query(F.data == 'statistic_month')
async def statistic_month(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StatisticData.month_and_year)

    temp_message = await callback.message.edit_text(AdminStats.ASK_MONTH,
                                    reply_markup=kb.get_month_selector_keyboard())

    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)
    await callback.answer()


@router.message(StatisticData.month_and_year)
async def handle_month_text(message: Message, state: FSMContext):
    if not validate_month(message.text):
        await message.delete()
        temp_message = await message.answer(AdminStats.ASK_MONTH_YEAR)
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)

        return
    
    from_date = dt(int(message.text.split(' ')[-1]), month_numbers.get(message.text.split(' ')[0].capitalize()), 1)
    to_date = from_date+relativedelta(months=1)-relativedelta(days=1)

    await state.update_data(from_date=from_date, to_date=to_date)

    await message.delete()
    await temp_message_repo.clear_temp_message_ids(message.from_user.id, message.chat.id, bot)

    await message.answer(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)


@router.callback_query(F.data.startswith('select_month_'))
async def handle_month_btn(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StatisticData.month_and_year)

    month = callback.data.split('_')[-1]
    current_date = dt.now()
    prev_month_last_day_date = current_date - timedelta(days=current_date.day)
    # последний_день_позапрошлого_месяца
    two_months_ago_last_day_date = prev_month_last_day_date - timedelta(days=prev_month_last_day_date.day)

    if month=='current':
        await state.update_data(
            from_date=current_date-timedelta(days=current_date.day+1),
            to_date=current_date
        )
        await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)   
    elif month=='prev':
        await state.update_data(
            from_date=prev_month_last_day_date-timedelta(days=prev_month_last_day_date.day-1),
            to_date=prev_month_last_day_date
        )
        await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)
    elif month=='last':
        await state.update_data(
            from_date=two_months_ago_last_day_date-timedelta(days=two_months_ago_last_day_date.day-1),
            to_date=two_months_ago_last_day_date
        )
        await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)
        
    await callback.answer()


@router.callback_query(F.data == 'custom_period')
async def statistic_custom_period(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StatisticData.custom_period)

    temp_message = await callback.message.edit_text(AdminStats.ASK_CUSTOM_PERIOD, reply_markup=kb.kb_cancel_select)
    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)

    await callback.answer('')


@router.message(StatisticData.custom_period)
async def handle_custom_period_text(message: Message, state: FSMContext):
    try:
        start_period = dt.strptime(message.text.split(' - ')[0], '%d.%m.%Y')
    except:
        await message.delete()

        temp_message = await message.answer(AdminStats.INVALID_FROM_DATE)
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)

        return
    
    try:
        end_period = dt.strptime(message.text.split(' - ')[1], '%d.%m.%Y')
    except:
        await message.delete()

        temp_message = await message.answer(AdminStats.INVALID_TO_DATE)
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)

        return
    
    if start_period > end_period:
        temp_message = await message.answer(AdminStats.CORRECT_DATE)
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)

        await temp_message_repo.add_temp_message_id(message.from_user.id, message.message_id)

        return 
    
    await state.update_data(from_date=start_period, to_date=end_period)

    await message.delete()

    await temp_message_repo.clear_temp_message_ids(message.from_user.id, message.chat.id, bot)
    
    await message.answer(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)

   
@router.callback_query(F.data == 'statistic_quarter')
async def statistic_quarter(callback : CallbackQuery, state: FSMContext):
    await state.set_state(StatisticData.quarter)
    temp_message = await callback.message.edit_text(AdminStats.ASK_QUARTER, reply_markup=kb.get_quarter_select_keybord())
    
    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)


    await callback.answer()


@router.callback_query(F.data.startswith('select_quarter_'))
async def handle_quarter_btn(callback : CallbackQuery, state: FSMContext):
    await state.set_state(StatisticData.quarter)

    from_date, to_date = quarter_to_date_range(callback.data.split('_')[-1])
    await state.update_data(from_date=from_date, to_date=to_date)

    await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)

   
@router.callback_query(F.data == 'statistic_year')
async def statistic_year(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StatisticData.year)
    temp_message = await callback.message.edit_text(AdminStats.ASK_YEAR, reply_markup=kb.get_year_select_keyboard())

    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)

    await callback.answer()


@router.message(StatisticData.year)
async def handle_year_text(message: Message, state: FSMContext):
    if len(message.text) != 4:
        await message.delete()
        temp_message = await message.answer(Common.ERROR_OCCURRED)   

        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)
        return
    
    await message.delete()

    await state.update_data(from_date=dt(int(message.text), 1, 1), to_date=dt(int(message.text), 12, 31))

    await temp_message_repo.clear_temp_message_ids(message.from_user.id, message.chat.id, bot)
    await message.answer(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)


@router.callback_query(F.data.startswith('select_year_'))
async def handle_year_btn(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StatisticData.year)

    current_date = dt.now()
    current_year = current_date.year
    name_year = callback.data.split('_')[-1]

    if name_year == 'last':
        year = current_year-2
    elif name_year == 'prev':
        year = current_year-1
    elif name_year == 'current':
        year=current_year
    
    await state.update_data(from_date=dt(year, 1, 1), to_date=dt(year, 12, 31))
    await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)


@router.callback_query(F.data == 'cancel_select')
async def cancel_select(callback: CallbackQuery):
    await callback.message.edit_text('📈 Выберите интересуемый период:', reply_markup=kb.kb_menu_statistics)

    await temp_message_repo.clear_temp_message_ids(callback.from_user.id, callback.message.chat.id, bot)


@router.callback_query(F.data=='short_report')
async def short_report(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    await callback.message.edit_text(AdminStats.REPORT_GENERATING_SHORT_CUSTOM, parse_mode='Markdown')

    purchases = await purchases_repo.find_by_date(data['from_date'], data['to_date'])

    await state.clear()
    await callback.message.edit_text(generate_short_report(purchases), parse_mode='Markdown')


@router.callback_query(F.data == 'excel')
async def excel_report(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await callback.message.edit_text(AdminStats.REPORT_GENERATING_FULL_CUSTOM, parse_mode='Markdown')

    purchases = await purchases_repo.find_by_date(data['from_date'], data['to_date'])

    if purchases:
        excel_report_file_path =  f'app/temp_docs/{callback.from_user.id}.xls'

        generate_excel_report(purchases, excel_report_file_path)

        await callback.message.answer_document(FSInputFile(excel_report_file_path))

        await state.clear()
        os.remove(excel_report_file_path)

    else:
        await callback.message.edit_text(AdminStats.NO_REPORT)

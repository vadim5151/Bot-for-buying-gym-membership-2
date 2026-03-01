import os
from datetime import datetime as dt, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext

from init import bot
from formatters import format_subscription
import app.keyboards as kb
from services.excel_reports import generate_excel_report
from database.repository import PurchasesRepository, TempMessageRepository
from app.messages import AdminStats, Common



router = Router()

purchases_repo = PurchasesRepository()
temp_message_repo = TempMessageRepository()


class Data(StatesGroup):
    quarter = State()
    from_date = State()
    to_date = State()
    date=State()
    month_name=State()
    year=State()
    custom_period = State()




@router.message(F.text == 'Статистика 📊')
async def menu_statistics(message: Message):
    await message.delete()

    await message.answer(AdminStats.MENU_TITLE, reply_markup=kb.kb_menu_statistics)


@router.callback_query(F.data == 'statistic_month')
async def statistic_month_func(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Data.date)

    temp_message = await callback.message.edit_text(AdminStats.ASK_MONTH,
                                    reply_markup=kb.get_month_selector_keyboard())

    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)

    await callback.answer()


@router.message(Data.date)
async def handle_month_callback(message: Message, state: FSMContext):
    month_names = {
        1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 
        5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
        9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
    }
     
    if message.text and len(message.text.split(' '))==2 and (isinstance(message.text.split(' ')[0], str) and message.text.split(' ')[-1].isdigit()):
        date = None
        for count, month_name in month_names.items():
            if message.text.split(' ')[0].capitalize() == month_name:         
                date = dt(int(message.text.split(' ')[-1]), count, 1)

        if date is not None:
            await state.update_data(date=date, month_name=message.text.split(' ')[0], year=message.text.split(' ')[-1])
        else:
            temp_message = await message.answer(Common.ERROR_OCCURRED)
            
            await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)

            return
        
        await message.delete()

        await temp_message_repo.clear_temp_message_ids(message.from_user.id, message.chat.id, bot)
    
        await message.answer(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)
    
    else:
        await message.delete()
        temp_message = await message.answer(AdminStats.ASK_MONTH_YEAR)
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)



@router.callback_query(F.data.startswith('select_month_'))
async def handle_month_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Data.date)

    month = callback.data.split('_')[-1]

    current_date = dt.now()

    current_year = current_date.year
    current_month = current_date.month

    month_names = {
        1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 
        5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
        9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
    }

    current_month_name = month_names.get(current_month, '')

    prev_month_date = current_date - timedelta(days=current_date.day)
    last_month_date = prev_month_date - timedelta(days=prev_month_date.day)

    prev_month_name = month_names.get(prev_month_date.month, '')
    last_month_name = month_names.get(last_month_date.month, '')

    if month=='current':   
        await state.update_data(date=current_date,month_name=current_month_name, year=current_year)
        await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)
        

    elif month=='prev':
        await state.update_data(date=prev_month_date,month_name=prev_month_name, year=prev_month_date.year)
        await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)

    elif month=='last':
        await state.update_data(date=last_month_date,month_name=last_month_name, year=last_month_date.year)
        await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)
        
    await callback.answer()


@router.callback_query(F.data == 'custom_period')
async def create_custom_period(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Data.custom_period)

    temp_message = await callback.message.edit_text(AdminStats.ASK_CUSTOM_PERIOD, reply_markup=kb.kb_cancel_select)
    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)


    await callback.answer('')


@router.message(Data.custom_period)
async def create_custom_period(message: Message, state: FSMContext):
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
        upd_start_period = end_period
        upd_end_period = start_period

        await state.update_data(from_date=upd_start_period, to_date=upd_end_period)
        temp_message = await message.answer(AdminStats.CORRECT_DATE.format(from_date=upd_start_period.strftime("%d.%m.%Y"), to_date=upd_end_period.strftime("%d.%m.%Y")))

        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)


        await message.delete()

        await temp_message_repo.clear_temp_message_ids(message.from_user.id, message.chat.id, bot)


        await message.answer(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)

    else:     
        await state.update_data(from_date=start_period, to_date=end_period)

        await message.delete()

        await temp_message_repo.clear_temp_message_ids(message.from_user.id, message.chat.id, bot)
        

        await message.answer(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)


@router.callback_query(F.data == 'statistic_quarter')
async def handle_quarter_callback(callback : CallbackQuery, state: FSMContext):
    await state.set_state(Data.quarter)
    temp_message = await callback.message.edit_text(AdminStats.ASK_QUARTER, reply_markup=kb.get_quarter_select_keybord())
    
    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)


    await callback.answer()


# @router.message(Data.quarter)
# async def handle_quarter_callback(message: Message, state: FSMContext):
#     if message.text and len(message.text.split(' '))==2 and (isinstance(message.text.split(' ')[0]) and isinstance(message.text.split(' ')[1])):
#         await message.delete()

#         await state.update_data(quarter=message.text)

        #  await temp_message_repo.clear_temp_message_ids(message.from_user.id, message.chat.id, bot)
#        

#         await message.answer(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)

#     else:   
#         await message.delete()

#         temp_message = await message.answer(Common.ERROR_OCCURRED)
            
#         await add_temp_message_id(message.from_user.id, temp_message.message_id)

#         return


@router.callback_query(F.data.startswith('select_quarter_'))
async def handle_quarter_callback(callback : CallbackQuery, state: FSMContext):
    await state.set_state(Data.quarter)

    quarter = callback.data.split('_')[-1]

    if quarter.split('-')[0] == 'I':
        await state.update_data(quarter=quarter.replace('I', '1'). replace('-', ' '))
        await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)

    elif quarter.split('-')[0] == 'II':
        await state.update_data(quarter=quarter.replace('II', '2'). replace('-', ' '))
        await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)

    elif quarter.split('-')[0] == 'III':
        await state.update_data(quarter=quarter.replace('III', '3'). replace('-', ' '))
        await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)

    elif quarter.split('-')[0] == 'IV':
        await state.update_data(quarter=quarter.replace('IV', '4'). replace('-', ' '))
        await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)

   
@router.callback_query(F.data == 'statistic_year')
async def handle_year_calback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Data.year)
    temp_message = await callback.message.edit_text(AdminStats.ASK_YEAR, reply_markup=kb.get_year_select_keyboard())

    await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)

    await callback.answer()


@router.message(Data.year)
async def handle_year_callback(message: Message, state: FSMContext):
    if message.text and len(message.text) == 4:
        await message.delete()

        await state.update_data(year=message.text)

        await temp_message_repo.clear_temp_message_ids(message.from_user.id, message.chat.id, bot)


        await message.answer(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)

    else:   
        await message.delete()

        temp_message = await message.answer(Common.ERROR_OCCURRED)
            
        await temp_message_repo.add_temp_message_id(message.from_user.id, temp_message.message_id)


        return


@router.callback_query(F.data.startswith('select_year_'))
async def handle_year_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Data.quarter)

    current_date = dt.now()

    current_year = current_date.year

    name_year = callback.data.split('_')[-1]

    if name_year == 'last':
        await state.update_data(year=current_year-2)
        await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)
    elif name_year == 'prev':
        await state.update_data(year=current_year-1)
        await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)
    elif name_year == 'current':
            await state.update_data(year=current_year)
            await callback.message.edit_text(AdminStats.CHOOSE_REPORT_FORMAT, reply_markup=kb.kb_formatter_report)
    else:
        await callback.message.edit_text(Common.ERROR_OCCURRED)
        


@router.callback_query(F.data=='short_report')
async def generation_report(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if 'from_date' in data:
        from_date = data['from_date'].strftime('%d.%m.%Y')
        to_date = data['to_date'].strftime('%d.%m.%Y')
        
        await callback.message.edit_text(AdminStats.REPORT_GENERATING_SHORT_CUSTOM.format(from_date=from_date, to_date=to_date), parse_mode='Markdown')
        
        text = f'*Отчет от {from_date} до  {to_date}*'

        all_purchases = []
        
        purchases = await purchases_repo.find_by_date(from_date)
        if purchases:
            for purchase in purchases:
                all_purchases.append(purchase)

        for i in range(1, (data['to_date']-data['from_date']).days+1):
            date = data['from_date'] + timedelta(days=i)
            purchases = await purchases_repo.find_by_date(date.strftime('%d.%m.%Y'))

            if purchases:
                for purchase in purchases:
                    all_purchases.append(purchase)

        await state.clear()

    elif 'date' in data:
        month = dt.strftime(data['date'], '%m')
        date = f"\\.{month}\\.{data['year']}$"

        text = f'*Отчет за {month} {data['year']}*'

        await callback.message.edit_text(AdminStats.REPORT_GENERATING_SHORT_MONTH.format(month=month, year=data['year']), parse_mode='Markdown')
        
        
        all_purchases = await purchases_repo.find_by_date({"$regex": date})
        
        await state.clear()


    elif 'quarter' in data:
        data = data['quarter']
        quarter = data.split(' ')[0]

        from_date_str = ''
        to_date_str = ''

        if data.split(' ')[0] == '1':
            quarter = quarter.replace('1', 'I')

            from_date_str += f'01.01.{data.split(' ')[1]}'
            to_date_str += f'31.03.{data.split(' ')[1]}'

        elif data.split(' ')[0] == '2':
            quarter = quarter.replace('2', 'II')

            from_date_str += f'01.04.{data.split(' ')[1]}'
            to_date_str += f'30.06.{data.split(' ')[1]}'

        elif data.split(' ')[0] == '3':
            quarter = quarter.replace('3', 'III')

            from_date_str += f'01.07.{data.split(' ')[1]}'
            to_date_str += f'30.09.{data.split(' ')[1]}'

        elif data.split(' ')[0] == '4':
            quarter = quarter.replace('4', 'IV')

            from_date_str += f'01.10.{data.split(' ')[1]}'
            to_date_str += f'31.12.{data.split(' ')[1]}'

        from_date_quarter = dt.strptime(from_date_str, '%d.%m.%Y')
        to_date_quarter = dt.strptime(to_date_str, '%d.%m.%Y')

        await callback.message.edit_text(AdminStats.REPORT_GENERATING_SHORT_QUARTER.format(quarter=quarter, count=data.split(' ')[1]), parse_mode='Markdown')
        
        text = f'*Отчет за {quarter}-Квартал {data.split(' ')[1]}*'

        all_purchases = []

        purchases = await purchases_repo.find_by_date(from_date_quarter)

        if purchases:
            for purchase in purchases:
                all_purchases.append(purchase)

        for i in range(1, (to_date_quarter-from_date_quarter).days+1):
            date = from_date_quarter + timedelta(days=i)

            purchases = await purchases_repo.find_by_date(date.strftime('%d.%m.%Y'))
            if purchases:
                for purchase in purchases:
                    all_purchases.append(purchase)
        await state.clear()


    elif 'year' in data:
        year = data['year']
        date = f"\\.{year}"

        await callback.message.edit_text(AdminStats.REPORT_GENERATING_SHORT_YEAR.format(year=year), parse_mode='Markdown')
        
        text = f'*Отчет за {year}*'

        all_purchases = await purchases_repo.find_by_date({'$regex': date})

        await state.clear()


    total_spent = 0
    total_buy_subscription = 0
    all_subscription = {}

    for purshases in all_purchases:
        total_buy_subscription += 1
        total_spent += purshases['subscription_price']

        if purshases['subscription_name'] in all_subscription and purshases['subscription_price'] in all_subscription:
            all_subscription[purshases['subscription_name']] += 1
        else:
            all_subscription.update({purshases['subscription_name']:1, purshases['subscription_price']:1})

    text += f'''
{format_subscription(all_purchases)}

Всего продано абонементов: *{total_buy_subscription}*
На сумму: *{total_spent:_}₽*
    '''

    await state.clear()
    await callback.message.edit_text(text, parse_mode='Markdown')


@router.callback_query(F.data == 'cancel_select')
async def cancel_select(callback: CallbackQuery):
    await callback.message.edit_text('📈 Выберите интересуемый период:', reply_markup=kb.kb_menu_statistics)


@router.callback_query(F.data == 'excel')
async def create_excel_report(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if 'from_date' in data:
        from_date = data['from_date'].strftime('%d.%m.%Y')
        to_date = data['to_date'].strftime('%d.%m.%Y')
        
        await callback.message.edit_text(AdminStats.REPORT_GENERATING_FULL_CUSTOM.format(from_date=from_date, to_date=to_date), parse_mode='Markdown')

        all_purchases = []

        purchases = await purchases_repo.find_by_date(from_date)

        if purchases:
            for purchase in purchases:
                all_purchases.append(purchase)

        for i in range(1, (data['to_date']-data['from_date']).days+1):
            date = data['from_date'] + timedelta(days=i)

    
            purchases = await purchases_repo.find_by_date(date.strftime('%d.%m.%Y'))
            if purchases:
                for purchase in purchases:
                    all_purchases.append(purchase)

        await state.clear()

    elif 'date' in data:
        month = dt.strftime(data['date'], '%m')
        date = f"\\.{month}\\.{data['year']}$"

        text = f'*Отчет за {month} {data['year']}*'

        await callback.message.edit_text(AdminStats.REPORT_GENERATING_FULL_MONTH.format(month=month, year=data['year']), parse_mode='Markdown')
        all_purchases = await purchases_repo.find_by_date({"$regex": date})
        
        await state.clear()

    elif 'quarter' in data:
        data = data['quarter']
        quarter = data.split(' ')[0]

        from_date_str = ''
        to_date_str = ''

        if data.split(' ')[0] == '1':
            quarter = quarter.replace('1', 'I')

            from_date_str += f'01.01.{data.split(' ')[1]}'
            to_date_str += f'31.03.{data.split(' ')[1]}'

        elif data.split(' ')[0] == '2':
            quarter = quarter.replace('2', 'II')

            from_date_str += f'01.04.{data.split(' ')[1]}'
            to_date_str += f'30.06.{data.split(' ')[1]}'

        elif data.split(' ')[0] == '3':
            quarter = quarter.replace('3', 'III')

            from_date_str += f'01.07.{data.split(' ')[1]}'
            to_date_str += f'30.09.{data.split(' ')[1]}'

        elif data.split(' ')[0] == '4':
            quarter = quarter.replace('4', 'IV')

            from_date_str += f'01.10.{data.split(' ')[1]}'
            to_date_str += f'31.12.{data.split(' ')[1]}'

        from_date_quarter = dt.strptime(from_date_str, '%d.%m.%Y')
        to_date_quarter = dt.strptime(to_date_str, '%d.%m.%Y')

        await callback.message.edit_text(AdminStats.REPORT_GENERATING_FULL_QUARTER.format(quarter=quarter, count=data.split(' ')[1]), parse_mode='Markdown')
        
        text = f'*Отчет за {quarter}-Квартал {data.split(' ')[1]}*'

        all_purchases = []
        purchases = await purchases_repo.find_by_date({"$regex": from_date_quarter})

        if purchases:
            for purchase in purchases:
                all_purchases.append(purchase)

        for i in range(1, (to_date_quarter-from_date_quarter).days+1):
            date = from_date_quarter + timedelta(days=i)
          
            purchases =   await purchases_repo.find_by_date(date.strftime('%d.%m.%Y'))
            if purchases:
                for purchase in purchases:
                    all_purchases.append(purchase)
        await state.clear()

    elif 'year' in data:
        year = data['year']
        date = f"\\.{year}"

        temp_message = await callback.message.edit_text(AdminStats.REPORT_GENERATING_FULL_YEAR(year=year), parse_mode='Markdown')
        
        await temp_message_repo.add_temp_message_id(callback.from_user.id, temp_message.message_id)

     
        all_purchases = await purchases_repo.find_by_date({'$regex': date})

        await state.clear()
    
    if all_purchases:
        excel_report_file_path =  f'app/temp_docs/{callback.from_user.id}.xls'

        generate_excel_report(all_purchases, excel_report_file_path)

        await callback.message.answer_document(FSInputFile(excel_report_file_path))

        await state.clear()
        os.remove(excel_report_file_path)

    else:
        await callback.message.edit_text(AdminStats.NO_REPORT)

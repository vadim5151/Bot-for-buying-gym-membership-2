from datetime import datetime as dt, timedelta

from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder


from utils import quarter_num_to_names, month_names



def create_user_btn_price_list(months):
    builder = InlineKeyboardBuilder()
    for month in sorted(months):
        if month == 1:
            builder.button(text=f'Купить {month} месяц', callback_data=f'buy_{month}_month')
        elif month>1 and month<5:
            builder.button(text=f'Купить {month} месяца', callback_data=f'buy_{month}_month')
        else:
            builder.button(text=f'Купить {month} месяцев', callback_data=f'buy_{month}_month')
    builder.adjust(1)
    return builder.as_markup()


def create_admin_price_list(months):
    builder = InlineKeyboardBuilder()
    for month in sorted(months):
        if month == 1:
            builder.button(text=f'редактировать {month} месяц 📝', callback_data=f'edit_{month}_month')
        elif month>1 and month<5:
            builder.button(text=f'редактировать {month} месяца 📝', callback_data=f'edit_{month}_month')
        else:
            builder.button(text=f'редактировать {month} месяцев 📝', callback_data=f'edit_{month}_month')
    builder.button(text='Добавить период 🗓️➕', callback_data='update_price')
    builder.adjust(1)
    return builder.as_markup()


def setting_notifications_payment_kb(available_periods, user_periods):
    builder = InlineKeyboardBuilder()

    for available_period in available_periods:
        if available_period == 1:
            builder.button(text=f'За день {"✅" if available_period in user_periods else "❌"}', callback_data='toggle_1')
        elif available_period == 7:    
            builder.button(text=f'За неделю {"✅" if available_period in user_periods else "❌"}', callback_data='toggle_7')
        elif available_period == 14:
            builder.button(text=f'За 2 недели {"✅" if available_period in user_periods else "❌"}', callback_data='toggle_14')
        elif available_period == 30 or available_period == 31:
            builder.button(text=f'За месяц {"✅" if available_period in user_periods else "❌"}', callback_data=f'toggle_{available_period}')
        elif 2<=available_period<5:
            builder.button(text=f'За {available_period} дня  {"✅" if available_period in user_periods else "❌"}', callback_data=f'toggle_{available_period}')
        else:
            builder.button(text=f'За {available_period} дней {"✅" if available_period in user_periods else "❌"}', callback_data=f'toggle_{available_period}')

    builder.adjust(1)
    return builder.as_markup()


def get_main_menu_keyboards(isAdmin:bool):
    user_menu = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Прайс'), KeyboardButton(text='Остатки по тарифу')],
        [KeyboardButton(text='Настройка уведомлений'), KeyboardButton(text='Мой профиль')]
    ], resize_keyboard=True)
        
    admin_menu = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Редактирование прайса 🔧 ')], 
        [KeyboardButton(text='Статистика 📊')]
    ], resize_keyboard=True)

    if isAdmin == True:
        return admin_menu
    else:
        return user_menu


def get_month_selector_keyboard():

    current_date = dt.now()

    current_year = current_date.year
    current_month = current_date.month

    current_month_name = month_names.get(current_month, '')

    prev_month_date = current_date - timedelta(days=current_date.day)
    prev_prev_month_date = prev_month_date - timedelta(days=prev_month_date.day)

    prev_month_name = month_names.get(prev_month_date.month, '')
    prev_prev_month_name = month_names.get(prev_prev_month_date.month, '')

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=f'{prev_prev_month_name} {prev_prev_month_date.year}', callback_data='select_month_last'),
        InlineKeyboardButton(text=f'{prev_month_name} {prev_month_date.year}', callback_data='select_month_prev'),
        InlineKeyboardButton(text=f'{current_month_name} {current_year}', callback_data='select_month_current')
    )

    builder.row(
        InlineKeyboardButton(text='Отмена', callback_data='cancel_select'),
    )

    return builder.as_markup()


def get_quarter_select_keybord():
    current_date = dt.now()
    current_year = current_date.year
    current_month = current_date.month

    current_quarter_num = current_month//3 if current_month%3==0 else current_month//3+1
    one_quarter_num_ago = current_quarter_num - 1 if current_quarter_num>1 else 4
    two_quarter_num_ago = one_quarter_num_ago - 1 if one_quarter_num_ago>1 else 4
    three_quarter_num_ago = two_quarter_num_ago - 1 if two_quarter_num_ago>1 else 4

    quarters = []
    for quarter_num in [three_quarter_num_ago, two_quarter_num_ago, one_quarter_num_ago, current_quarter_num]:
        quarters.append(f'{quarter_num_to_names[quarter_num]}-{current_year-1 if quarter_num>current_quarter_num else current_year}')

    builder = InlineKeyboardBuilder()
    quarter_buttons = []
    for quarter in quarters:
        quarter_buttons.append(InlineKeyboardButton(text=f'{quarter}', callback_data=f'select_quarter_{quarter}'))
    
    builder.row(*quarter_buttons)
    builder.row(
        InlineKeyboardButton(text='Отмена', callback_data='cancel_select'),
    )
    return builder.as_markup()


def get_year_select_keyboard():
    current_date = dt.now()

    current_year = current_date.year

    prev_year = current_year - 1
    last_year = prev_year - 1

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=f'{last_year}', callback_data='select_year_last'),
        InlineKeyboardButton(text=f'{prev_year}', callback_data='select_year_prev'),
        InlineKeyboardButton(text=f'{current_year}', callback_data='select_year_current')
    )

    builder.row(
        InlineKeyboardButton(text='Отмена', callback_data='cancel_select'),
    )

    return builder.as_markup()


kb_cancel_select = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='cancel_select')]
])

kb_cancel_edit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='cancel_edit')]
])

kb_formatter_report = InlineKeyboardMarkup(inline_keyboard=[
    [
    InlineKeyboardButton(text='Excel', callback_data='excel'), 
    InlineKeyboardButton(text='Сокращенный отчет', callback_data='short_report')
    ]
])

kb_edit_price_list = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Удалить 🗑️', callback_data='remove_price'), 
        InlineKeyboardButton(text='Изменить ✏️', callback_data='update_price'),
        InlineKeyboardButton(text='Отмена ❌', callback_data='cancel_edit')
    ]
])

kb_menu_statistics = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Месяц 📅', callback_data='statistic_month'), 
        InlineKeyboardButton(text='Квартал 📊', callback_data='statistic_quarter'),
        InlineKeyboardButton(text='Год 📈', callback_data='statistic_year')
    ],
    [
        InlineKeyboardButton(text='Ввести свой период', callback_data='custom_period')
    ]
    
])

confirmation_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Да хочу', callback_data='confirm_purchase')],
    [InlineKeyboardButton(text="❌ Нет, не хочу", callback_data="cancel_purchase")]
])

extend_membership = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продлить абонемент', callback_data='extend_membership')]
])

notification_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Уведомления об оплате', callback_data='setting_notification_payment')],
    [InlineKeyboardButton(text='Уведомления о новостях', callback_data='setting_notofication_news')]
])

change_registration = InlineKeyboardMarkup(inline_keyboard=[
    [
    InlineKeyboardButton(text='Изменить ФИО', callback_data='change_fio'),
    InlineKeyboardButton(text='Изменить дату рождения', callback_data='change_date_of_birth')
    ]
])
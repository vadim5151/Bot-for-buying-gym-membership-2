from datetime import datetime
from dateutil.relativedelta import relativedelta 



month_names = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
}

month_numbers = {value: key for key, value in month_names.items()}

quarter_names_to_num = {
    'I':1, 'II':2, 'III':3, 'IV':4
}

quarter_num_to_names = {value: key for key, value in quarter_names_to_num.items()}

def quarter_to_date_range(quarter_str: str) -> datetime:
    quarter_name, year = quarter_str.split('-')
    quarter = quarter_names_to_num.get(quarter_name)
    # вычисление месяца начала квартала
    start_month = (quarter-1)*3+1

    from_date = datetime(int(year), start_month, 1)
    to_date = from_date + relativedelta(months=3) - relativedelta(days=1)

    return from_date, to_date
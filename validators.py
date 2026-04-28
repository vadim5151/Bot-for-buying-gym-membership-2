from datetime import datetime

from dateutil.relativedelta import relativedelta 

from exceptions import InvalidFullName, InvalidFullNameWordCounts, FutureBirthDate, AgeLimit, InvalidDateFormat



MIN_AGE = 5      
MAX_AGE = 120    


def validate_full_name(full_name):
    parts = full_name.split(' ')

    for part in parts:
        if not (part.istitle() and part.isalpha()):
            raise InvalidFullName

    if len(parts) != 3 and len(parts) != 2:
        raise InvalidFullNameWordCounts


def validate_birthdate(date_str):
    try:
        birth_date = datetime.strptime(date_str.strip(), "%d.%m.%Y")
    except ValueError:
        raise InvalidDateFormat
    today = datetime.now()
    age = relativedelta(today, birth_date).years

    if age < 0:
        raise FutureBirthDate
    if age > MAX_AGE:
        raise AgeLimit


def validate_price_period(message_text):
    return message_text and len(message_text.split()) == 2 and (message_text.split()[0].isdigit() and message_text.split()[1].isdigit())


def validate_month(message_text):
    return message_text and len(message_text.split(' '))==2 and message_text.split(' ')[-1].isdigit()
      
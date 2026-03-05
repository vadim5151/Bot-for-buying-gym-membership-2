from datetime import datetime

from dateutil.relativedelta import relativedelta 

from exceptions import InvalidFullName, InvalidFullNameWordCounts, FutureBirthDate, AgeLimit



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
        raise

    today = datetime.now()

    age = relativedelta(today, birth_date)

    if age < 0:
        raise FutureBirthDate

    if age > MAX_AGE:
        raise AgeLimit
    


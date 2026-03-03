from datetime import datetime

from app.messages import User



MIN_AGE = 5      
MAX_AGE = 120    


def validate_full_name(full_name):
    """
    Проверяет, что строка содержит три слова, каждое с заглавной буквы.
    Возвращает (True, None) если корректно, иначе (False, сообщение об ошибке).
    """
   
    parts = full_name.split(' ')
 
    if len(parts) == 3 or len(parts) == 2:
    
        for part in parts:
            if not (part.istitle() and part.isalpha()):
                return False, User.INVALID_FULLNAME
    else:
        return False, "ФИО должно состоять из трёх слов или двух слов (если нет отчества)"

    return True, None


def validate_birthdate(date_str):
    """
    Проверяет строку с датой рождения.
    Возвращает (True, datetime объект) если успешно,
    иначе (False, сообщение об ошибке).
    """
    try:
        birth_date = datetime.strptime(date_str.strip(), "%d.%m.%Y")
    except ValueError:
        return False, User.INVALID_DATE_FORMAT
    
    today = datetime.now()
    
    if birth_date > today:
        return False, User.FUTURE_BIRTHDATE
    
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    if age < MIN_AGE:
        return False, f"Возраст не может быть меньше {MIN_AGE} лет"
    if age > MAX_AGE:
        return False, f"Возраст не может быть больше {MAX_AGE} лет"
    
    return True, birth_date

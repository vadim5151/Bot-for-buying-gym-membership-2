import asyncio
import sys
import time
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from dateutil.relativedelta import relativedelta 

sys.path.append('../../database')
sys.path.append('../../')

from requests_bd import collection_users, collection_user_waiting_alerts # type: ignore
from config import TG_TOKEN

#TODO Одна функ записывает в коллекцию id которым надо отправить аллерт прям щас А второя функ читает эту коллекцию и отправляет 
#TODO try-except 
#TODO если у пользователя 0 или меньше дней?

async def fetch_user_for_payment_alerts():
    while True:
        today_date = datetime.today()
        users = await collection_users.find(filter={}).to_list()
        print(users)

        for user in users:
            print(user)
            days_left = (datetime.strptime(user['expiration_date'], "%d.%m.%Y") - today_date).days
            print(days_left)

            if days_left in user['notification_days_period']:
                await collection_user_waiting_alerts.insert_one({'tg_id': user['tg_id'], 'days_left': days_left})

        asyncio.sleep(60)




asyncio.run(fetch_user_for_payment_alerts())


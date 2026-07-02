import asyncio
from datetime import datetime
import logging

import pymongo

from database.repositories.user_repository import UserRepository
from database.repositories.waiting_alerts_repository import WaitingAlertsRepository
from config import PAYMENT_ENDS_CHECK_DELAY
from configs.logging_config import setup_logging



setup_logging()

user_repo = UserRepository()
alerts_repo = WaitingAlertsRepository()

logging.info(msg='Успешное подключение к бд')

async def fetch_user_for_payment_alerts():
    while True:
        today_date = datetime.today()
        users = await user_repo.get_all()
        for user in users:
            days_left = (user['expiration_date'] - today_date).days
            if days_left in user['notification_days_period'] or days_left==0:
                if await alerts_repo.find_one_by_id(user['tg_id']):
                    await alerts_repo.update_one(user['tg_id'], days_left)
                else:
                    try: 
                        await alerts_repo.insert_one(user['tg_id'], days_left)
                    except pymongo.errors.DuplicateKeyError:
                        logging.error(msg='Ошибка в дубликации ключа')
        logging.info(msg='Проверка окончания оплат совершена')
        await asyncio.sleep(PAYMENT_ENDS_CHECK_DELAY)


asyncio.run(fetch_user_for_payment_alerts())


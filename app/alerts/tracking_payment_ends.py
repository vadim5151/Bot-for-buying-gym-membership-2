import asyncio
from datetime import datetime

import pymongo

from database.requests_bd import collection_user_waiting_alerts # type: ignore
from database.repository import PurchasesRepository, UserRepository, WaitingAlertsRepository


#TODO try-except 
#TODO если у пользователя 0 или меньше дней?
purchases_repo = PurchasesRepository()
user_repo = UserRepository()
alerts_repo = WaitingAlertsRepository()


async def fetch_user_for_payment_alerts():
    while True:
        today_date = datetime.today()
        purchases = await purchases_repo.get_all()
        users = await user_repo.get_all()

        for purchase, user in zip(purchases, users):
            days_left = (purchase['expiration_date'] - today_date).days
            if days_left in user['notification_days_period'] or days_left==0:
                if await alerts_repo.find_one_by_id(user['tg_id']):
                    await alerts_repo.update_one(user['tg_id'], days_left)
                else:
                    try: 
                        await alerts_repo.insert_one(user['tg_id'], days_left)
                    except pymongo.errors.DuplicateKeyError:
                        print('Ашибка в дубликации ключа')
# сделать проверку раз в день
        await asyncio.sleep(10)


asyncio.run(fetch_user_for_payment_alerts())


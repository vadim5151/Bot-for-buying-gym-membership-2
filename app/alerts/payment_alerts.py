import asyncio
import sys


from motor.motor_asyncio import AsyncIOMotorClient
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties


sys.path.append('../../')

from config import TG_TOKEN



def format_payment_alerts(days_left):
    print(type(days_left))
    print(days_left)
    text = 'До окончания вашего абонемента'

    if days_left == 1:
        text+='остался 1 день'
    elif 1<days_left<5:
        text+=f'осталось {days_left} дня'
    elif days_left>5:
        text+=f'осталось {days_left} дней'

    return text


async def main():
    bot = Bot(token=TG_TOKEN,  default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    client = AsyncIOMotorClient('localhost', port=27017)

    conn = client['Bot_for_buying_gym_membership']
    collection_user_waiting_alerts = conn['User_waiting_alerts']
    print('Успех')

    async with collection_user_waiting_alerts.watch(full_document='updateLookup') as change_stream:
        async for change in change_stream:
            print(change)

            if change['operationType'] == 'insert':
                tg_id = change['fullDocument']['tg_id']
                days_left = change['fullDocument']['days_left']

                await bot.send_message(chat_id=tg_id, text=format_payment_alerts(days_left))

                collection_user_waiting_alerts.delete_one(filter={'tg_id':tg_id})


if __name__ == '__main__':
    asyncio.run(main())
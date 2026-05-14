import asyncio

from motor.motor_asyncio import AsyncIOMotorClient
from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import TG_TOKEN



BOT = Bot(token=TG_TOKEN,  default=DefaultBotProperties(parse_mode=ParseMode.HTML))
_client = AsyncIOMotorClient('localhost', port=27017)
_conn = _client['Bot_for_buying_gym_membership']
COLLECTION_USER_WAITING_ALERTS = _conn['User_waiting_alerts']


def format_payment_alerts(days_left):
    text = 'До окончания вашего абонемента'
    if days_left == 1:
        text+='остался 1 день'
    elif 1<days_left<5:
        text+=f'осталось {days_left} дня'
    elif days_left>5:
        text+=f'осталось {days_left} дней'
    return text

async def send_notification(tg_id: int, days_left: int) -> None:
    try:
        await BOT.send_message(chat_id=tg_id, text=format_payment_alerts(days_left))
        COLLECTION_USER_WAITING_ALERTS.delete_one(filter={'tg_id': tg_id})
    except TelegramBadRequest as e:
        print(f'Не удалось отправить уведомление по id: {tg_id}\n{e.message}')
        if e.message == 'Bad Request: chat not found':
            COLLECTION_USER_WAITING_ALERTS.delete_one(filter={'tg_id': tg_id})

#Если нормальные названия переменых, то комментарии не нужны - Боб Мартин так и писал!!!
async def process_old_doc() -> None:
    all_doc = await COLLECTION_USER_WAITING_ALERTS.find().to_list()
    for doc in all_doc:
        tg_id = doc['tg_id']
        days_left = doc['days_left']
        await send_notification(tg_id, days_left)


async def main():
    await process_old_doc()
    async with COLLECTION_USER_WAITING_ALERTS.watch(full_document='updateLookup') as change_stream:
        async for change in change_stream:
            if change['operationType'] == 'insert':
                tg_id = change['fullDocument']['tg_id']
                days_left = change['fullDocument']['days_left']
                await send_notification(tg_id, days_left)



if __name__ == '__main__':
    asyncio.run(main())
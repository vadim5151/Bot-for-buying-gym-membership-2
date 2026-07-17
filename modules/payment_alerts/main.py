import asyncio
import logging

from motor.motor_asyncio import AsyncIOMotorClient
from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from configs.tg_bot_config import TG_TOKEN
from configs.logging_config import setup_logging
from configs.db_config import db_alerts_uri



setup_logging()

BOT = Bot(token=TG_TOKEN,  default=DefaultBotProperties(parse_mode=ParseMode.HTML))
_client = AsyncIOMotorClient(db_alerts_uri)
_conn = _client['bgm_alerts']
COLLECTION_USER_WAITING_ALERTS = _conn['User_waiting_alerts']
logging.info(msg='Успешное подключение к бд')

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
    logging.info(msg='Сообщения начали отправляться.')
    try:
        await BOT.send_message(chat_id=tg_id, text=format_payment_alerts(days_left))
        COLLECTION_USER_WAITING_ALERTS.delete_one(filter={'tg_id': tg_id})
    except TelegramBadRequest as e:
        logging.error(msg=f'Не удалось отправить уведомление по id: {tg_id}\n{e.message}')
        if e.message == 'Bad Request: chat not found':
            logging.info(msg='Пользователь удалил чат с ботом')
            COLLECTION_USER_WAITING_ALERTS.delete_one(filter={'tg_id': tg_id})


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
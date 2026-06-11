import asyncio
import logging

from aiogram import Dispatcher

from init import bot
from app.handlers.admin_handlers.price_edit_handlers import router as price_edit_router
from app.handlers.admin_handlers.statistic_handlers import router as statistic_router
from app.handlers.user_handlers.start import router as start_router
from app.handlers.user_handlers.registration import router as registration_router
from app.handlers.user_handlers.buy import router as buy_router
from app.handlers.user_handlers.notifications import router as notifications_router
from app.handlers.user_handlers.profile import router as profile_router
from app.handlers.admin_handlers.notification_edit_handlers import router as notifications_edit_router
from configs.logging_config import setup_logging


dp = Dispatcher()


async def main():
    setup_logging()

    dp.include_router(statistic_router)
    dp.include_router(price_edit_router)
    dp.include_router(start_router)
    dp.include_router(registration_router)
    dp.include_router(buy_router)
    dp.include_router(notifications_router)
    dp.include_router(profile_router)
    dp.include_router(notifications_edit_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info(msg='Выход из программы')
    
    
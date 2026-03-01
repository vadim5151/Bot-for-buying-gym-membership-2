import asyncio

from aiogram import Dispatcher

from init import bot
from app.handlers.admin_handlers.price_edit_handlers import router as price_edit_router
from app.handlers.admin_handlers.statistic_handlers import router as statistic_router
from app.handlers.user_handlers.start import router as start_router
from app.handlers.user_handlers.registration import router as registration_router
from app.handlers.user_handlers.buy import router as buy_router
from app.handlers.user_handlers.notifications import router as notifications_router
from app.handlers.user_handlers.profile import router as profile_router



dp = Dispatcher()


async def main():
    dp.include_router(statistic_router)
    dp.include_router(price_edit_router)
    dp.include_router(start_router)
    dp.include_router(registration_router)
    dp.include_router(buy_router)
    dp.include_router(notifications_router)
    dp.include_router(profile_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
    
    
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession

from config import TG_TOKEN, PROXY_URL


session = AiohttpSession(proxy=PROXY_URL)
bot = Bot(token=TG_TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
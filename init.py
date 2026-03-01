from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import TG_TOKEN



bot = Bot(token=TG_TOKEN,  default=DefaultBotProperties(parse_mode=ParseMode.HTML))
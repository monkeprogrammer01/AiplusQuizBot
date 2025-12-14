from aiogram import Bot, Dispatcher

from bot.handlers import common
from config import BOT_TOKEN

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

dp.include_router(common.router)
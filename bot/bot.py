from aiogram import Bot, Dispatcher

from bot.handlers import common, quiz_create, quiz_send
from config import BOT_TOKEN

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

dp.include_router(common.router)
dp.include_router(quiz_create.router)
dp.include_router(quiz_send.router)
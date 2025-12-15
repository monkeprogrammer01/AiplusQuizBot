from aiogram import types, Router
from aiogram.types import Message, InputFile
import random
from aiogram.filters import CommandStart, Command

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Чтобы создать quiz напиши /create_quiz")

@router.message(Command('is_alikhan_gay'))
async def temp(message: Message):
    p = random.randint(95, 100)
    await message.answer(f"Алихан гей на {p} процентов")

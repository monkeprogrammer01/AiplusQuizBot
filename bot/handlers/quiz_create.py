from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InputFile
import random
from aiogram.filters import CommandStart, Command
from bot.storage import quiz

router = Router()

class CreateQuiz(StatesGroup):
    waiting_for_title = State()
    waiting_for_question = State()

@router.message(Command("create_quiz"))
async def create_quiz(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Название куиза")
    await state.set_state(CreateQuiz.waiting_for_title)

@router.message(CreateQuiz.waiting_for_title)
async def quiz_title_entered(message: Message, state: FSMContext):
    title = message.text

    quiz = await create_quiz(
        owner_id=message.from_user.id,
        title=title
    )

    await state.update_data(quiz_id=quiz.id)

    await message.answer(
        f"Квиз «{title}» создан \nТеперь введи первый вопрос:"
    )
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonPollType
from aiogram.filters import Command
from bot.storage.quiz import add_question, add_option, create_quiz_in_db

router = Router()

quiz_control_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать вопрос", request_poll=KeyboardButtonPollType(type="quiz"))],
        [KeyboardButton(text="Завершить куиз")],
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)

class CreateQuiz(StatesGroup):
    waiting_for_title = State()
    waiting_for_question = State()
    waiting_for_option = State()

@router.message(Command("create_quiz"))
async def create_quiz(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Название куиза")
    await state.set_state(CreateQuiz.waiting_for_title)

@router.message(CreateQuiz.waiting_for_title)
async def quiz_title_entered(message: Message, state: FSMContext):
    title = message.text

    quiz = await create_quiz_in_db(
        owner_id=message.from_user.id,
        title=title
    )

    await state.update_data(quiz_id=quiz.id)

    await message.answer(
        f"Квиз «{title}» создан \nТеперь введи первый вопрос:",
        reply_markup=quiz_control_kb
    )
    await state.set_state(CreateQuiz.waiting_for_question)

@router.message(lambda m: m.poll is not None)
async def poll_received(message: Message, state: FSMContext):
    poll = message.poll


    if poll.type != "quiz":
        await message.answer("Нужен именно quiz")
        return

    data = await state.get_data()
    quiz_id = data.get("quiz_id")

    if not quiz_id:
        await message.answer("Сначала создай куиз")
        return

    question = await add_question(
        quiz_id=quiz_id,
        text=poll.question,
        poll_id=poll.id
    )

    for idx, option in enumerate(poll.options):
        await add_option(
            question_id=question.id,
            text=option.text,
            is_correct=(idx == poll.correct_option_id)
        )

    await message.answer("Вопрос сохранён \nМожешь создать ещё один или /done")

@router.message(lambda m: m.text == "Завершить куиз")
async def finish_quiz(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Куиз завершён",
        reply_markup=types.ReplyKeyboardRemove()
    )

@router.message(lambda m: m.text == "Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Действие отменено",
        reply_markup=types.ReplyKeyboardRemove()
    )
from db import AsyncSessionLocal
from models import Quiz, Question, Answer, Option
from sqlalchemy.future import select

async def create_quiz(owner_id, title):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            quiz = Quiz(owner_id=owner_id, title=title)
            session.add(quiz)
            await session.flush()
            return quiz

async def get_quiz(quiz_id: int) -> Quiz | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Quiz).where(Quiz.id == quiz_id)
        )
        quiz = result.scalars().first()
        return quiz

async def add_question(quiz_id: int, text: str, photo_url: str | None = None) -> Question:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            question = Question(quiz_id=quiz_id, text=text)
            if photo_url:
                question.photo_url = photo_url
            session.add(question)
            await session.flush()
            return question

async def add_option(question_id: int, text: str, is_correct: bool = False) -> Option:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            option = Option(question_id=question_id, text=text, is_correct=is_correct)
            session.add(option)
            await session.flush()
            return option

async def save_answer(user_id: int, question_id: int, selected_option_id: int) -> Answer:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Option).where(Option.id == selected_option_id)
            )
            option = result.scalars().first()
            is_correct = option.is_correct if option else False

            answer = Answer(
                user_id=user_id,
                question_id=question_id,
                selected_option_id=selected_option_id,
                is_correct=is_correct
            )
            session.add(answer)
            await session.flush()
            return answer

async def get_quiz_with_questions(quiz_id: int) -> Quiz | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Quiz).where(Quiz.id == quiz_id)
        )
        quiz = result.scalars().first()
        return quiz
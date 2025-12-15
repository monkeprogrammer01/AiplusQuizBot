import asyncio
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.storage.quiz import get_quizzes, get_quiz, get_full_quiz

router = Router()


@router.message(Command("my_quizzes"))
async def my_quizzes(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer(
            "Эта команда работает только в группах!\n\n"
            "Добавьте меня в группу и используйте там."
        )
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    quizzes = await get_quizzes(user_id)

    if not quizzes:
        await message.answer("У вас пока нет квизов")
        return

    builder = InlineKeyboardBuilder()

    for quiz in quizzes:
        builder.button(
            text=f"📋 {quiz.title}",
            callback_data=f"sendquiz_{quiz.id}_{chat_id}"
        )

    builder.adjust(1)

    await message.answer(
        f"Ваши квизы (отправка в эту группу):\n\n"
        f"Группа: {message.chat.title}\n"
        f"ID группы: {chat_id}\n\n"
        f"Выберите квиз для отправки:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(lambda c: c.data.startswith("sendquiz_"))
async def process_quiz_selection(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer("Ошибка в данных", show_alert=True)
        return

    quiz_id = int(parts[1])
    chat_id = int(parts[2])

    await callback.message.edit_text("щящя минутку...")

    quiz_data = await get_full_quiz(quiz_id)

    if not quiz_data:
        await callback.message.edit_text("Куиз не найден")
        return

    quiz = quiz_data['quiz']
    questions = quiz_data['questions']

    if not questions:
        await callback.message.edit_text("В этом куизе нет вопросов")
        return

    if quiz.owner_id != callback.from_user.id:
        await callback.message.edit_text("Вы не владелец этого куиза")
        return

    sent_count = 0
    total_questions = len(questions)

    for i, q_data in enumerate(questions, 1):
        question = q_data['question']
        options = q_data['options']

        if i % 5 == 0 or i == total_questions:
            await callback.message.edit_text(
                f"📤 Отправляю квиз «{quiz.title}»...\n"
                f"Прогресс: {i}/{total_questions}"
            )

        if not options:
            continue

        option_texts = []
        correct_option_id = None

        for idx, option in enumerate(options):
            option_texts.append(option.text)
            if option.is_correct:
                correct_option_id = idx

        if correct_option_id is None:
            continue

        try:
            await callback.bot.send_poll(
                chat_id=chat_id,
                question=question.text,
                options=option_texts,
                type="quiz",
                correct_option_id=correct_option_id,
                is_anonymous=False,
                allows_multiple_answers=False,
                explanation=f"Вопрос {i} из {total_questions}" if total_questions > 1 else None
            )
            sent_count += 1

            await asyncio.sleep(0.5)

        except Exception as e:
            error_msg = str(e).lower()

            if "not enough rights" in error_msg or "need administrator rights" in error_msg:
                await callback.message.edit_text(
                    "*Ошибка прав доступа!*\n\n"
                    "У бота недостаточно прав для отправки опросов.\n\n"
                    "Что нужно сделать:\n"
                    "1. Сделать бота администратором группы\n"
                    "2. Дать права:\n"
                    "   • Отправка сообщений\n"
                    "   • Создание опросов\n\n"
                    "После этого попробуйте снова.",
                    parse_mode="Markdown"
                )
                return

            elif "chat not found" in error_msg:
                await callback.message.edit_text(
                    "*Группа не найдена!*\n\n"
                    "Бот не может найти указанную группу.\n"
                    "Убедитесь, что бот добавлен в группу.",
                    parse_mode="Markdown"
                )
                return

            else:
                print(f"Ошибка при отправке вопроса {i}: {e}")
                continue

    if sent_count > 0:
        success_text = (
            f"*Куиз успешно отправлен!*\n\n"
            f"*Название:* {quiz.title}\n"
            f"*Отправлено вопросов:* {sent_count}/{total_questions}\n"
            f"*В группу:* {callback.message.chat.title}"
        )

        builder = InlineKeyboardBuilder()
        builder.button(
            text="Отправить ещё раз",
            callback_data=f"sendquiz_{quiz.id}_{chat_id}"
        )
        builder.button(
            text="Выбрать другой квиз",
            callback_data="back_to_list"
        )
        builder.adjust(1)

        await callback.message.edit_text(
            success_text,
            parse_mode="Markdown",
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.edit_text(
            "*Не удалось отправить ни одного вопроса*\n\n"
            "Возможные причины:\n"
            "1. Бот не администратор группы\n"
            "2. Нет прав на отправку опросов\n"
            "3. Все вопросы не имеют правильных ответов\n"
            "4. Техническая ошибка Telegram",
            parse_mode="Markdown"
        )


@router.callback_query(lambda c: c.data == "back_to_list")
async def back_to_quizzes_list(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id

    quizzes = await get_quizzes(user_id)

    if not quizzes:
        await callback.message.edit_text("❌ У вас больше нет квизов")
        return

    builder = InlineKeyboardBuilder()

    for quiz in quizzes:
        builder.button(
            text=f"📋 {quiz.title}",
            callback_data=f"sendquiz_{quiz.id}_{chat_id}"
        )

    builder.adjust(1)

    await callback.message.edit_text(
        f"📚 Ваши квизы (отправка в эту группу):\n\n"
        f"Группа: {callback.message.chat.title}\n"
        f"ID группы: {chat_id}\n\n"
        f"Выберите квиз для отправки:",
        reply_markup=builder.as_markup()
    )


@router.message(Command("lastquiz"))
async def send_last_quiz(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("Эта команда работает только в группах!")
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    quizzes = await get_quizzes(user_id)

    if not quizzes:
        await message.answer("У вас нет квизов")
        return

    last_quiz = quizzes[0]

    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Отправить «{last_quiz.title}»",
        callback_data=f"sendquiz_{last_quiz.id}_{chat_id}"
    )

    await message.answer(
        f"*Последний куиз:* {last_quiz.title}\n\n"
        f"Отправить его в эту группу?",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )


@router.message(Command("check_rights"))
async def check_bot_rights(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("❌ Эта команда работает только в группах!")
        return

    try:
        me = await message.bot.get_me()
        chat_member = await message.bot.get_chat_member(
            chat_id=message.chat.id,
            user_id=me.id
        )

        if chat_member.status == "administrator":
            perms = chat_member.permissions
            rights_text = (
                f"✅ *Бот — администратор*\n\n"
                f"Права:\n"
                f"• 📝 Отправка сообщений: {'✅' if perms.can_send_messages else '❌'}\n"
                f"• 📊 Создание опросов: {'✅' if perms.can_send_polls else '❌'}\n"
                f"• 📎 Отправка медиа: {'✅' if perms.can_send_media_messages else '❌'}\n"
                f"• 📌 Закрепление: {'✅' if perms.can_pin_messages else '❌'}"
            )

            if not perms.can_send_polls:
                rights_text += "\n\n⚠️ *Внимание!* Бот не может отправлять опросы!"

        else:
            rights_text = (
                f"❌ *Бот не администратор*\n\n"
                f"Статус: {chat_member.status}\n\n"
                f"Для отправки куизов нужно:\n"
                f"1. Сделать бота администратором\n"
                f"2. Дать права на отправку сообщений и опросов"
            )

        await message.answer(rights_text, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
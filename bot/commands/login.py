import re

from sqlmodel import select
from telebot.types import Message

from bot.enum import BotMessages
from db.database import get_session
from db.models import User


def get_user(chat_id):
    with get_session() as session:
        return (
            session.exec(select(User).where(User.chat_id == chat_id)).first(),
            session,
        )


def update_username_if_needed(user, username, session):
    if not user.username and username:
        user.username = username
        session.add(user)
        session.commit()


def handle_email_stage(bot, chat_id, user, text, session):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", text):
        bot.send_message(chat_id, BotMessages.INVALID_EMAIL.value)
        return
    user.email = text
    user.stage = "waiting_phone"
    session.add(user)
    session.commit()
    bot.send_message(chat_id, BotMessages.EMAIL_SAVED.value)


def handle_phone_stage(bot, chat_id, user, text, session):
    if not (text.isdigit() and len(text) == 11):
        bot.send_message(chat_id, BotMessages.INVALID_PHONE.value)
        return
    user.phone = text
    user.stage = "waiting_password"
    session.add(user)
    session.commit()
    bot.send_message(chat_id, BotMessages.PHONE_SAVED.value)


def handle_password_stage(bot, chat_id, user, text, session):
    if len(text) < 14:
        bot.send_message(chat_id, BotMessages.PASSWORD_TOO_SHORT.value)
        return
    if not re.search(r"[a-z]", text):
        bot.send_message(chat_id, BotMessages.PASSWORD_NO_LOWERCASE.value)
        return
    if not re.search(r"\d", text):
        bot.send_message(chat_id, BotMessages.PASSWORD_NO_DIGIT.value)
        return
    user.password = text
    user.stage = "done"
    session.add(user)
    session.commit()
    bot.send_message(chat_id, BotMessages.PASSWORD_SAVED.value)


def login_command(bot, message: Message):
    chat_id = message.chat.id
    username = message.from_user.username
    text = message.text.strip()

    user, session = get_user(chat_id)
    if not user:
        bot.send_message(chat_id, BotMessages.USER_NOT_FOUND.value)
        return

    update_username_if_needed(user, username, session)

    if user.stage == "waiting_email":
        handle_email_stage(bot, chat_id, user, text, session)
    elif user.stage == "waiting_phone":
        handle_phone_stage(bot, chat_id, user, text, session)
    elif user.stage == "waiting_password":
        handle_password_stage(bot, chat_id, user, text, session)
    elif user.stage == "done":
        bot.send_message(chat_id, BotMessages.ALREADY_DONE.value)

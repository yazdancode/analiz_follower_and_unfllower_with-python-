import os

from instagrapi import Client
from sqlmodel import select
from telebot.types import Message

from bot.enum import BotMessages
from db.database import get_session
from db.models import User

pending_2fa = {}


def connect_instagram(bot, message: Message):
    chat_id = message.chat.id

    with get_session() as session:
        user = session.exec(select(User).where(User.chat_id == chat_id)).first()

        if not user:
            bot.send_message(chat_id, BotMessages.LOGIN_REQUIRED.value)
            return

        if user.stage != "done":
            bot.send_message(chat_id, BotMessages.INCOMPLETE_INFO.value)
            return

    cl = Client()
    session_file = f"sessions/{user.chat_id}.json"
    if os.path.exists(session_file):
        cl.load_settings(session_file)

    try:
        print("📥 Email from DB:", user.email)
        print("🔑 Password from DB:", user.password)
        cl.login(user.email, user.password)
        bot.send_message(
            chat_id, BotMessages.CONNECTED.value.format(username=user.username)
        )
        cl.dump_settings(session_file)

    except Exception as e:
        if "Two-factor authentication required" in str(e):
            bot.send_message(chat_id, BotMessages.TWO_FACTOR_REQUIRED.value)
            pending_2fa[chat_id] = cl
        else:
            bot.send_message(chat_id, BotMessages.CONNECT_FAILED.value.format(error=e))

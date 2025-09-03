import os
import random
import time

from instagrapi import Client
from sqlmodel import select
from telebot.types import Message

from bot.enum import BotMessages
from db.database import get_session
from db.models import User

pending_2fa = {}


def get_user_from_db(chat_id):
    with get_session() as session:
        return session.exec(select(User).where(User.chat_id == chat_id)).first()


def send_login_stage_messages(bot, chat_id, user):
    if not user:
        bot.send_message(chat_id, BotMessages.LOGIN_REQUIRED.value)
        return False
    if user.stage != "done":
        bot.send_message(chat_id, BotMessages.INCOMPLETE_INFO.value)
        return False
    return True


def setup_instagram_client(user, proxy=None):
    cl = Client()
    if proxy:
        cl.set_proxy(proxy)

    os.makedirs("sessions", exist_ok=True)
    username = user.username or f"user_{user.chat_id}"
    session_file = f"sessions/{username.lower()}.json"

    if os.path.exists(session_file):
        cl.load_settings(session_file)

    return cl, session_file


def handle_login_and_profile(bot, chat_id, cl, user, session_file):
    cl.login(user.email, user.password)
    cl.dump_settings(session_file)

    bot.send_message(
        chat_id, BotMessages.CONNECTED.value.format(username=user.username)
    )

    time.sleep(random.uniform(2, 5))  # تأخیر طبیعی

    profile = cl.user_info_by_username(user.username.lower())
    bot.send_message(
        chat_id,
        f"👤 نام کامل: {profile.full_name}\n"
        f"📸 تعداد پست‌ها: {profile.media_count}\n"
        f"👥 دنبال‌کننده‌ها: {profile.follower_count}\n"
        f"👤 دنبال‌شونده‌ها: {profile.following_count}",
    )

    time.sleep(random.uniform(10, 30))  # تأخیر طبیعی دوم


def handle_login_errors(bot, chat_id, e, cl):
    error_msg = str(e)

    if "Two-factor authentication required" in error_msg:
        bot.send_message(chat_id, BotMessages.TWO_FACTOR_REQUIRED.value)
        pending_2fa[chat_id] = cl

    elif "Facebook" in error_msg or "blacklist" in error_msg:
        bot.send_message(chat_id, BotMessages.IP_BLOCKED.value)

    else:
        bot.send_message(
            chat_id, BotMessages.CONNECT_FAILED.value.format(error=error_msg)
        )


def connect_instagram(bot, message: Message, proxy: str | None = None):
    chat_id = message.chat.id
    user = get_user_from_db(chat_id)

    if not send_login_stage_messages(bot, chat_id, user):
        return

    cl, session_file = setup_instagram_client(user, proxy)

    try:
        handle_login_and_profile(bot, chat_id, cl, user, session_file)
    except Exception as e:
        handle_login_errors(bot, chat_id, e, cl)

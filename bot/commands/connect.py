import os
import random
import time

from instagrapi import Client
from sqlmodel import select
from telebot.types import Message

from bot.enum import BotMessages
from db.database import get_session
from db.models import User

# نگه‌داری کلاینت‌های در انتظار Two-Factor
pending_2fa = {}


def connect_instagram(bot, message: Message, proxy: str | None = None):
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
    if proxy:
        cl.set_proxy(proxy)
    os.makedirs("sessions", exist_ok=True)
    session_file = f"sessions/{user.username.lower()}.json"
    if os.path.exists(session_file):
        cl.load_settings(session_file)

    try:
        cl.login(user.email, user.password)
        cl.dump_settings(session_file)
        bot.send_message(
            chat_id, BotMessages.CONNECTED.value.format(username=user.username)
        )
        time.sleep(random.randint(2, 5))

        try:
            profile = cl.user_info_by_username(user.username.lower())
            bot.send_message(
                chat_id,
                f"👤 نام کامل: {profile.full_name}\n"
                f"📸 تعداد پست‌ها: {profile.media_count}\n"
                f"👥 دنبال‌کننده‌ها: {profile.follower_count}\n"
                f"👤 دنبال‌شونده‌ها: {profile.following_count}\n",
            )
        except Exception as e:
            bot.send_message(chat_id, f"❌ خطا در دریافت اطلاعات پروفایل: {e}")

        time.sleep(random.randint(10, 30))

    except Exception as e:
        error_msg = str(e)
        if "Two-factor authentication required" in error_msg:
            bot.send_message(chat_id, BotMessages.TWO_FACTOR_REQUIRED.value)
            pending_2fa[chat_id] = cl
        elif "Facebook" in error_msg or "blacklist" in error_msg:
            bot.send_message(
                chat_id,
                "❌ آی‌پی شما توسط اینستاگرام بلاک شده یا باید با فیسبوک وارد شوید.\n"
                "➡️ راه‌حل: تغییر IP یا لاگین از طریق اپلیکیشن رسمی.",
            )
        else:
            bot.send_message(
                chat_id, BotMessages.CONNECT_FAILED.value.format(error=error_msg)
            )

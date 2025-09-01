from telebot.types import Message
from sqlmodel import select
from db.database import get_session
from db.models import User
from instagrapi import Client
import os

# دیکشنری برای کاربرانی که در انتظار 2FA هستند
pending_2fa = {}


def connect_instagram(bot, message: Message):
    chat_id = message.chat.id

    with get_session() as session:
        user = session.exec(select(User).where(User.chat_id == chat_id)).first()

        if not user:
            bot.send_message(
                chat_id, "❌ ابتدا باید اطلاعات خود را ثبت کنید. /login را بزنید."
            )
            return

        if user.stage != "done":
            bot.send_message(
                chat_id,
                "❌ هنوز اطلاعات شما کامل ثبت نشده است. لطفاً مراحل login را تمام کنید.",
            )
            return

    cl = Client()
    session_file = f"sessions/{user.chat_id}.json"
    if os.path.exists(session_file):
        cl.load_settings(session_file)

    try:
        cl.login(user.email, user.password)
        bot.send_message(
            chat_id, f"✅ اینستاگرام شما متصل شد!\nیوزرنیم: {user.username}"
        )
        cl.dump_settings(session_file)

    except Exception as e:
        if "Two-factor authentication required" in str(e):
            bot.send_message(
                chat_id,
                "⚠️ ورود نیاز به کد تایید دو مرحله‌ای دارد.\n"
                "لطفاً کدی که به ایمیل یا شماره موبایل شما ارسال شده را وارد کنید.",
            )
            pending_2fa[chat_id] = cl
        else:
            bot.send_message(chat_id, f"❌ اتصال به اینستاگرام موفق نبود:\n{e}")

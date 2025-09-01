from telebot.types import Message
from sqlmodel import select
from db.database import get_session
from db.models import User
from instagrapi import Client

def connect_instagram(bot, message: Message):
    chat_id = message.chat.id

    with get_session() as session:
        user = session.exec(select(User).where(User.chat_id == chat_id)).first()

        if not user:
            bot.send_message(chat_id, "❌ ابتدا باید اطلاعات خود را ثبت کنید. /login را بزنید.")
            return

        if user.stage != "done":
            bot.send_message(chat_id, "❌ هنوز اطلاعات شما کامل ثبت نشده است. لطفاً مراحل login را تمام کنید.")
            return

        # لاگین به اینستاگرام با اطلاعات کاربر
        try:
            cl = Client()
            cl.login(user.email, user.password)
            bot.send_message(chat_id, f"✅ اینستاگرام شما با موفقیت متصل شد!\nیوزرنیم: {user.username}")
        except Exception as e:
            bot.send_message(chat_id, f"❌ اتصال به اینستاگرام موفق نبود:\n{e}")

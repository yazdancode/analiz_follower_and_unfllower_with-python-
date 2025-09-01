from telebot.types import Message
from sqlmodel import select
from db.database import get_session
from db.models import User
from bot.enum import BotMessages


def login_command(bot, message: Message):
    chat_id = message.chat.id
    username = message.from_user.username
    text = message.text

    with get_session() as session:
        user = session.exec(select(User).where(User.chat_id == chat_id)).first()
        if not user:
            bot.send_message(chat_id, "❌ ابتدا باید عضو کانال شوید و /start را بزنید.")
            return

        # ثبت یوزرنیم تلگرام
        if not user.username:
            user.username = username

        # مرحله ایمیل
        if user.stage == "waiting_email":
            user.email = text
            user.stage = "waiting_phone"
            session.add(user)
            session.commit()
            bot.send_message(
                chat_id, "✅ ایمیل ثبت شد. لطفاً شماره تلفن خود را وارد کنید:"
            )
            return

        # مرحله شماره تماس
        if user.stage == "waiting_phone":
            user.phone = text
            user.stage = "waiting_password"
            session.add(user)
            session.commit()
            bot.send_message(
                chat_id, "✅ شماره تلفن ثبت شد. لطفاً پسورد خود را وارد کنید:"
            )
            return

        # مرحله پسورد
        if user.stage == "waiting_password":
            user.password = text
            user.stage = "done"
            session.add(user)
            session.commit()
            bot.send_message(
                chat_id, "✅ اطلاعات شما کامل ثبت شد. ممنون که همراه ما هستید!"
            )
            return

        # اگر اطلاعات قبلاً ثبت شده
        if user.stage == "done":
            bot.send_message(chat_id, BotMessages.ALREADY_DONE.value)

import re

from sqlmodel import select
from telebot.types import Message

from bot.enum import BotMessages
from db.database import get_session
from db.models import User


def login_command(bot, message: Message):
    chat_id = message.chat.id
    username = message.from_user.username
    text = message.text.strip()

    with get_session() as session:
        user = session.exec(select(User).where(User.chat_id == chat_id)).first()
        if not user:
            bot.send_message(chat_id, "❌ ابتدا باید عضو کانال شوید و /start را بزنید.")
            return

        # ثبت یوزرنیم تلگرام اگر خالی است
        if not user.username and username:
            user.username = username
            session.add(user)
            session.commit()

        # مرحله ایمیل
        if user.stage == "waiting_email":
            email = text
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                bot.send_message(chat_id, "❌ ایمیل معتبر وارد کنید.")
                return
            user.email = email
            user.stage = "waiting_phone"
            session.add(user)
            session.commit()
            bot.send_message(
                chat_id, "✅ ایمیل ثبت شد. لطفاً شماره تلفن خود را وارد کنید:"
            )
            return

        # مرحله شماره تماس
        if user.stage == "waiting_phone":
            phone = text
            if not (phone.isdigit() and len(phone) == 11):
                bot.send_message(chat_id, "❌ شماره تلفن معتبر وارد کنید (11 رقم).")
                return
            user.phone = phone
            user.stage = "waiting_password"
            session.add(user)
            session.commit()
            bot.send_message(
                chat_id, "✅ شماره تلفن ثبت شد. لطفاً پسورد خود را وارد کنید:"
            )
            return

        # مرحله پسورد
        if user.stage == "waiting_password":
            password = text
            if len(password) < 14:
                bot.send_message(chat_id, "❌ پسورد باید حداقل 14 کاراکتر باشد.")
                return
            if not re.search(r"[a-z]", password):
                bot.send_message(chat_id, "❌ پسورد باید حداقل یک حرف کوچک داشته باشد.")
                return
            if not re.search(r"\d", password):
                bot.send_message(chat_id, "❌ پسورد باید حداقل یک عدد داشته باشد.")
                return
            user.password = password
            user.stage = "done"
            session.add(user)
            session.commit()
            bot.send_message(
                chat_id, "✅ اطلاعات شما کامل ثبت شد. ممنون که همراه ما هستید!"
            )
            return
        if user.stage == "done":
            bot.send_message(chat_id, BotMessages.ALREADY_DONE.value)

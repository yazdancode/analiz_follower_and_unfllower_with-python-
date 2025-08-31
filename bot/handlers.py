from telebot.types import Message
from telebot import TeleBot
from db.database import get_session
from db.models import User
from sqlmodel import select
from bot.keyboard import create_inline_keyboard
from bot.enum import BotMessages
from instagrapi import Client

CHANNEL_ID = "https://t.me/yazdancodeo"
ADMIN_CHAT_IDS = [5105508285]

def register_handlers(bot: TeleBot):
    cl = Client()  # Client یک بار ساخته می‌شود

    # هندلر دستور /start
    @bot.message_handler(commands=["start"])
    def start_handler(message: Message):
        chat_id = message.chat.id
        with get_session() as session:
            user = session.exec(select(User).where(User.chat_id == chat_id)).first()

        if user and user.stage == "done":
            # کاربر قبلاً ثبت و لاگین شده، فالورها را نشان بده
            try:
                cl.login(user.email, user.password)
                followers = cl.user_followers(cl.user_id)
                followers_list = [f.username for f in followers.values()][:10]  # ۱۰ فالور اول
                bot.send_message(
                    chat_id,
                    f"سلام دوباره! 😃\n"
                    f"شما قبلاً لاگین شده‌اید.\n"
                    f"تعداد فالورها: {len(followers)}\n"
                    f"نمونه ۱۰ فالور اول: {', '.join(followers_list)}"
                )
            except Exception as e:
                bot.send_message(chat_id, f"❌ لاگین اینستاگرام موفق نبود: {e}")
        else:
            bot.send_message(
                chat_id,
                BotMessages.START.value,
                reply_markup=create_inline_keyboard(),
            )

    # هندلر تایید عضویت
    @bot.callback_query_handler(func=lambda call: call.data == "confirm_membership")
    def confirm_handler(call):
        chat_id = call.message.chat.id
        if chat_id in ADMIN_CHAT_IDS:
            is_member = True
        else:
            try:
                status = bot.get_chat_member(CHANNEL_ID, chat_id).status
                is_member = status in ["creator", "administrator", "member"]
            except Exception:
                is_member = False

        with get_session() as session:
            user = session.exec(select(User).where(User.chat_id == chat_id)).first()

            if user:
                if not is_member:
                    session.delete(user)
                    session.commit()
                    bot.send_message(chat_id, BotMessages.LEFT_CHANNEL.value)
                else:
                    bot.answer_callback_query(call.id, BotMessages.ALREADY_MEMBER.value)
            else:
                if is_member:
                    user = User(chat_id=chat_id, stage="waiting_email")
                    session.add(user)
                    session.commit()
                    bot.answer_callback_query(call.id, BotMessages.ALREADY_MEMBER.value)
                    bot.send_message(chat_id, BotMessages.WELCOME.value)
                else:
                    bot.send_message(chat_id, BotMessages.NOT_MEMBER.value)

    # هندلر پیام‌های مرحله‌ای
    @bot.message_handler(func=lambda m: True)
    def message_handler(message: Message):
        chat_id = message.chat.id
        text = message.text

        with get_session() as session:
            user = session.exec(select(User).where(User.chat_id == chat_id)).first()
            if not user:
                bot.send_message(chat_id, BotMessages.REQUEST_INFO.value)
                return

            if user.stage == "waiting_email":
                user.email = text
                user.stage = "waiting_phone"
                session.add(user)
                session.commit()
                bot.send_message(chat_id, BotMessages.EMAIL_RECEIVED.value)

            elif user.stage == "waiting_phone":
                user.phone = text
                user.stage = "waiting_password"
                session.add(user)
                session.commit()
                bot.send_message(chat_id, BotMessages.PHONE_RECEIVED.value)

            elif user.stage == "waiting_password":
                user.password = text
                session.add(user)
                session.commit()
                bot.send_message(chat_id, BotMessages.PASSWORD_RECEIVED.value)

                # تلاش برای ورود به اینستاگرام و نمایش فالورها
                try:
                    cl.login(user.email, user.password)
                    user.stage = "done"
                    session.add(user)
                    session.commit()

                    followers = cl.user_followers(cl.user_id)
                    followers_list = [f.username for f in followers.values()][:10]
                    bot.send_message(
                        chat_id,
                        f"✅ ورود به اینستاگرام موفق بود!\n"
                        f"تعداد فالورها: {len(followers)}\n"
                        f"نمونه ۱۰ فالور اول: {', '.join(followers_list)}"
                    )

                except Exception as e:
                    bot.send_message(chat_id, f"❌ ورود به اینستاگرام موفق نبود: {e}")

            elif user.stage == "done":
                bot.send_message(chat_id, BotMessages.ALREADY_DONE.value)

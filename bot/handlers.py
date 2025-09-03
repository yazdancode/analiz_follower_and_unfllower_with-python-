from instagrapi import Client
from sqlmodel import select
from telebot import TeleBot
from telebot.types import Message

from bot.callbacks.membership import confirm_membership
from bot.commands.connect import connect_instagram, pending_2fa
from bot.commands.login import login_command
from bot.messages.start import start_handler
from db.database import get_session
from db.models import User


def register_handlers(bot: TeleBot):
    # /start
    @bot.message_handler(commands=["start"])
    def handle_start(message):
        start_handler(bot, message)

    # /login
    @bot.message_handler(commands=["login"])
    def handle_login(message):
        login_command(bot, message)

    # /connect
    @bot.message_handler(commands=["connect"])
    def handle_connect(message):
        connect_instagram(bot, message)

    # تایید عضویت
    @bot.callback_query_handler(func=lambda call: call.data == "confirm_membership")
    def handle_membership(call):
        confirm_membership(bot, call)

    # هندلر دریافت کد 2FA
    @bot.message_handler(func=lambda m: m.chat.id in pending_2fa)
    def handle_2fa_code(message: Message):
        chat_id = message.chat.id
        verification_code = message.text.strip()

        cl: Client = pending_2fa[chat_id]
        with get_session() as session:
            user = session.exec(select(User).where(User.chat_id == chat_id)).first()

            try:
                cl.set_user_agent(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                cl.timeout = 30
                cl.login(user.email, user.password, verification_code=verification_code)
                cl.dump_settings(f"sessions/{user.chat_id}.json")
                instagram_username = cl.username
                bot.send_message(
                    chat_id,
                    f"✅ اینستاگرام شما با موفقیت متصل شد!\nیوزرنیم: {instagram_username}",
                )
            except Exception as e:
                error_msg = f"❌ اتصال به اینستاگرام موفق نبود:\n{str(e)}"
                if "10061" in str(e):
                    error_msg += "\n\n⚠️ مشکل اتصال به اینترنت یا فایروال دارید"
                bot.send_message(chat_id, error_msg)
            finally:
                pending_2fa.pop(chat_id, None)

    @bot.message_handler(func=lambda m: True)
    def handle_message(message):
        if message.text.startswith("/"):
            return
        login_command(bot, message)

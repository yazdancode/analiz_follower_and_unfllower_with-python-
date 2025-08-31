from telebot.types import Message
from telebot import TeleBot
from db.database import get_session
from db.models import User
from sqlmodel import select
from bot.keyboard import create_inline_keyboard

CHANNEL_ID = "https://t.me/yazdancodeo"
ADMIN_CHAT_IDS = [5105508285]

def register_handlers(bot: TeleBot):
    @bot.message_handler(commands=["start"])
    def start_handler(message: Message):
        bot.send_message(
            message.chat.id,
            "سلام! برای ادامه روی عضویت بزنید.",
            reply_markup=create_inline_keyboard()
        )

    @bot.callback_query_handler(func=lambda call: call.data == "confirm_membership")
    def confirm_handler(call):
        chat_id = call.message.chat.id
        # بررسی عضویت
        if chat_id in ADMIN_CHAT_IDS:
            is_member = True
        else:
            try:
                status = bot.get_chat_member(CHANNEL_ID, chat_id).status
                is_member = status in ["creator", "administrator", "member"]
            except Exception:
                is_member = False

        with get_session() as session:
            existing_user = session.exec(select(User).where(User.chat_id == chat_id)).first()
            if existing_user:
                if not is_member:
                    session.delete(existing_user)
                    session.commit()
                    bot.send_message(chat_id, "❌ شما از کانال خارج شده‌اید.")
                else:
                    bot.answer_callback_query(call.id, "✅ شما قبلا عضو شده‌اید.")
            else:
                if is_member:
                    session.add(User(chat_id=chat_id))
                    session.commit()
                    bot.answer_callback_query(call.id, "✅ عضویت شما تایید شد!")
                else:
                    bot.send_message(chat_id, "❌ هنوز عضو کانال نیستید.")

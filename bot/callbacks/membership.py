from telebot.types import CallbackQuery
from sqlmodel import select
from db.database import get_session
from db.models import User
from bot.enum import BotMessages
from decouple import config

CHANNEL_ID = config("CHANNEL_ID")
ADMIN_CHAT_IDS = config("ADMIN_CHAT_IDS")

def confirm_membership(bot, call: CallbackQuery):
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
        existing_user = session.exec(select(User).where(User.chat_id == chat_id)).first()

        if existing_user:
            if not is_member:
                session.delete(existing_user)
                session.commit()
                bot.send_message(chat_id, BotMessages.LEFT_CHANNEL.value)
            else:
                bot.send_message(chat_id, BotMessages.ALREADY_MEMBER.value)
        else:
            if is_member:
                user = User(chat_id=chat_id, stage="waiting_email")
                session.add(user)
                session.commit()
                bot.send_message(chat_id, BotMessages.WELCOME.value)
            else:
                bot.send_message(chat_id, BotMessages.NOT_MEMBER.value)

from decouple import config
from sqlmodel import select
from telebot.apihelper import ApiTelegramException
from telebot.types import CallbackQuery

from bot.enum import BotMessages
from db.database import get_session
from db.models import User

CHANNEL_ID = config("CHANNEL_ID")
ADMIN_CHAT_IDS = [5105508285]


def check_membership(bot, chat_id):
    if chat_id in ADMIN_CHAT_IDS:
        return True
    try:
        status = bot.get_chat_member(CHANNEL_ID, chat_id).status
        return status in ["creator", "administrator", "member"]
    except ApiTelegramException:
        return False


def get_existing_user(chat_id):
    with get_session() as session:
        return (
            session.exec(select(User).where(User.chat_id == chat_id)).first(),
            session,
        )


def delete_user_and_notify(bot, chat_id, user, session):
    session.delete(user)
    session.commit()
    bot.send_message(chat_id, BotMessages.LEFT_CHANNEL.value)


def create_user_and_notify(bot, chat_id, session):
    user = User(chat_id=chat_id, stage="waiting_email")
    session.add(user)
    session.commit()
    bot.send_message(chat_id, BotMessages.WELCOME.value)


def confirm_membership(bot, call: CallbackQuery):
    chat_id = call.message.chat.id
    is_member = check_membership(bot, chat_id)
    user, session = get_existing_user(chat_id)

    if user:
        if not is_member:
            delete_user_and_notify(bot, chat_id, user, session)
        else:
            bot.send_message(chat_id, BotMessages.ALREADY_MEMBER.value)
    else:
        if is_member:
            create_user_and_notify(bot, chat_id, session)
        else:
            bot.send_message(chat_id, BotMessages.NOT_MEMBER.value)

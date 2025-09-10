import os
import time

from decouple import config
from dotenv import load_dotenv
from sqlmodel import select
from telebot.apihelper import ApiTelegramException
from telebot.types import CallbackQuery

from bot.constants import BotMessages
from db.database import get_session
from db.models import User

CHANNEL_ID = config("CHANNEL_ID")
load_dotenv()
ADMIN_CHAT_IDS = [int(os.environ.get("ADMIN_CHAT_IDS"))]


def check_membership(bot, chat_id, retries=3, delay=2):
    """Check if a user is a member of the channel, with retries for delay issues."""
    if chat_id in ADMIN_CHAT_IDS:
        return True

    for attempt in range(1, retries + 1):
        try:
            status = bot.get_chat_member(CHANNEL_ID, chat_id).status
            print(f"[Attempt {attempt}] User {chat_id} status: {status}")
            if status in ["creator", "administrator", "member"]:
                return True
        except ApiTelegramException as e:
            print(f"[Attempt {attempt}] ApiTelegramException: {e}")
        time.sleep(delay)

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
    user_id = call.from_user.id

    is_member = check_membership(bot, user_id)
    user, session = get_existing_user(chat_id)

    if session is None:
        bot.send_message(chat_id, BotMessages.ERROR_DATABASE.value)
        return

    if user and not is_member:
        delete_user_and_notify(bot, chat_id, user, session)

    elif not user and is_member:
        create_user_and_notify(bot, chat_id, session)

    elif not user and not is_member:
        bot.send_message(chat_id, BotMessages.LEFT_CHANNEL.value)

    elif user and is_member:
        bot.send_message(chat_id, BotMessages.ALREADY_MEMBER.value)

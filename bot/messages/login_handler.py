from telebot.types import Message

from bot.commands.login import (
    get_user,
    handle_email_stage,
    handle_password_stage,
    handle_phone_stage,
    update_username_if_needed,
)
from bot.enum import BotMessages


def login_command(bot, message: Message):
    """"""
    chat_id = message.chat.id
    username = message.from_user.username
    text = message.text.strip()

    user, session = get_user(chat_id)
    if not user:
        bot.send_message(chat_id, BotMessages.USER_NOT_FOUND.value)
        return

    update_username_if_needed(user, username, session)

    if user.stage == "waiting_email":
        handle_email_stage(bot, chat_id, user, text, session)
    elif user.stage == "waiting_phone":
        handle_phone_stage(bot, chat_id, user, text, session)
    elif user.stage == "waiting_password":
        handle_password_stage(bot, chat_id, user, text, session)
    elif user.stage == "done":
        bot.send_message(chat_id, BotMessages.ALREADY_DONE.value)

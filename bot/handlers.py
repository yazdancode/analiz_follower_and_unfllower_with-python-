from telebot import TeleBot

from bot.callbacks.membership import confirm_membership
from bot.commands.connect import connect_instagram
from bot.commands.login import login_command
from bot.messages.start import start_handler


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

    @bot.message_handler(func=lambda m: True)
    def handle_message(message):
        if message.text.startswith("/"):
            return
        login_command(bot, message)

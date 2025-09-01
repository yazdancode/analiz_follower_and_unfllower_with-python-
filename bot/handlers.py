from telebot import TeleBot
from bot.messages.start import start_handler
from bot.commands.login import login_command
from bot.callbacks.membership import confirm_membership
from bot.commands.connect import connect_instagram

def register_handlers(bot: TeleBot):

    # command /start
    @bot.message_handler(commands=["start"])
    def handle_start(message):
        start_handler(bot, message)

    # command /login
    @bot.message_handler(commands=["login"])
    def handle_login(message):
        login_command(bot, message)

    # command /connect
    @bot.message_handler(commands=["connect"])
    def handle_connect(message):
        connect_instagram(bot, message)

    # callback عضویت کانال
    @bot.callback_query_handler(func=lambda call: call.data == "confirm_membership")
    def handle_membership(call):
        confirm_membership(bot, call)

    # message_handler برای مراحل ورود (ایمیل، شماره، پسورد)
    @bot.message_handler(func=lambda m: True)
    def handle_message(message):
        # اجازه نده پیام‌هایی که دستور هستند دوباره به login_command بروند
        if message.text.startswith("/"):
            return
        login_command(bot, message)

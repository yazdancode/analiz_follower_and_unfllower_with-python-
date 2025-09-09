from telebot import TeleBot

from bot.callbacks.membership import confirm_membership
from bot.commands.help import help_handler
from bot.commands.login import get_user
from bot.commands.password_change import change_password_request, update_password
from bot.commands.profile_account import analyze_follower, profile
from bot.commands.remove_account import remove_account
from bot.enum import BotMessages
from bot.messages.connect_instagram_handler import connect_instagram
from bot.messages.login_handler import login_command
from bot.messages.logout import logout_handler
from bot.messages.start import start_handler


def register_handlers(bot: TeleBot):
    """
    ثبت هندلرهای پیام و کال‌بک برای ربات تلگرام.

    Args:
        bot (TeleBot): شیء ربات تلگرام برای مدیریت پیام‌ها و کال‌بک‌ها.

    هندلرهای ثبت‌شده:
        - /start: شروع تعامل با ربات و ارسال پیام خوش‌آمدگویی.
        - /login: آغاز فرآیند ورود کاربر به اینستاگرام.
        - /connect: اتصال به حساب اینستاگرام با اطلاعات ذخیره‌شده.
        - /help: نمایش راهنمای دستورات.
        - تایید عضویت: بررسی عضویت کاربر در کانال تلگرام.
        - پیام‌های متنی غیر دستوری: هدایت به فرآیند ورود یا نمایش پیام پیش‌فرض.
    """

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

    # /help
    @bot.message_handler(commands=["help"])
    def handle_help(message):
        help_handler(bot, message)

    # /logout
    @bot.message_handler(commands=["logout"])
    def handle_logout(message):
        logout_handler(bot, message, is_action=True)

    # /remove_account
    @bot.message_handler(commands=["remove"])
    def remove(message):
        remove_account(bot, message)

    # /account
    @bot.message_handler(commands=["account"])
    def account(message):
        profile(bot, message)

    # /change_password
    @bot.message_handler(commands=["change_password"])
    def change_password(message):
        change_password_request(bot, message)

    @bot.message_handler(commands=["analyze_follower"])
    def analyze(message):
        analyze_follower(message, bot)

    @bot.message_handler(func=lambda m: True)
    def handle_text_messages(message):
        chat_id = message.chat.id
        # text = message.text.strip()
        user, session = get_user(chat_id)
        if not user:
            bot.send_message(chat_id, BotMessages.USER_NOT_FOUND.value)
            return
        if user.stage == "waiting_new_password":
            update_password(bot, message)
            return
        login_command(bot, message)

    @bot.callback_query_handler(func=lambda call: call.data == "confirm_membership")
    def handle_membership(call):
        confirm_membership(bot, call)

    @bot.message_handler(func=lambda m: True)
    def handle_message(message):
        if not message.text:
            return

        if message.text.startswith("/"):
            return
        login_command(bot, message)

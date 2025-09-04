from telebot import TeleBot

from bot.callbacks.membership import confirm_membership
from bot.commands.help import help_handler
from bot.messages.connect_instagram_handler import connect_instagram
from bot.messages.login_handler import login_command
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

    # تایید عضویت
    @bot.callback_query_handler(func=lambda call: call.data == "confirm_membership")
    def handle_membership(call):
        confirm_membership(bot, call)

    # پیام‌های ناشناخته یا متنی
    @bot.message_handler(func=lambda m: True)
    def handle_message(message):
        if not message.text:  # جلوگیری از خطا در پیام‌های غیرمتنی
            return

        if message.text.startswith("/"):
            return  # دستور ناشناخته → فعلاً نادیده گرفته می‌شود

        # پیام متنی معمولی → هدایت به ورود
        login_command(bot, message)

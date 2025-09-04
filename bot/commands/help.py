from telebot.types import Message


def help_handler(bot, message: Message):
    """
    هندلر دستور /help برای ربات تلگرام.

    این تابع زمانی اجرا می‌شود که کاربر دستور /help را بفرستد
    و یک پیام راهنما شامل دستورات قابل استفاده در ربات برای او ارسال می‌کند.

    :param bot: شیء TeleBot برای ارسال پیام و ارتباط با API تلگرام.
    :param message: شیء Message که پیام ورودی کاربر را نشان می‌دهد.
    :return: None
    """
    bot.reply_to(
        message,
        "دستورات موجود:\n"
        "/start - شروع کار با ربات\n"
        "/login - ورود به ربات\n"
        "/connect - اتصال به اینستاگرام\n",
    )

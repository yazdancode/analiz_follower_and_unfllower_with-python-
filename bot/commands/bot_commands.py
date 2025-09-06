import telebot


def set_bot_commands(bot: telebot.TeleBot):
    """
    تنظیم دستورات پیش‌فرض ربات در منوی تلگرام.

    این دستورات وقتی کاربر روی آیکون "/" کلیک کند، نمایش داده می‌شوند.

    :param bot: شیء TeleBot برای ارتباط با API تلگرام.
    :return: None
    """
    bot.set_my_commands(
        commands=[
            telebot.types.BotCommand("start", "شروع ربات"),
            telebot.types.BotCommand("login", "ورود به حساب کاربری"),
            telebot.types.BotCommand("connect", "اتصال به اینستاگرام"),
            telebot.types.BotCommand("remove_account", "حذف حساب کاربری"),
            telebot.types.BotCommand("logout", "خروج از حساب کاربری"),
            telebot.types.BotCommand("help", "نمایش راهنما"),
        ]
    )

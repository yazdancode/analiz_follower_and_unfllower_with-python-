from telebot.types import Message


def help_handler(bot, message: Message):
    """
    هندلر دستور /help برای ربات تلگرام.

    پیام راهنما را با فرمت HTML (بدون CSS) برای کاربر ارسال می‌کند.
    """
    text = (
        "<b>📖 راهنمای ربات</b>\n\n"
        "<u>دستورات موجود:</u>\n\n"
        "• <code>/start</code> — شروع کار با ربات\n"
        "• <code>/login</code> — ورود به حساب کاربری\n"
        "• <code>/connect</code> — اتصال به اینستاگرام\n"
        "• <code>/remove</code> — حذف حساب کاربری\n"
        "• <code>/logout</code> — خروج از حساب کاربری\n"
        "• <code>/account</code> — نمایش اطلاعات حساب کاربری\n"
        "• <code>/change_password</code> — تغییر رمز عبور اینستاگرام\n"
        "• <code>/help</code> — نمایش همین راهنما\n"
    )

    bot.reply_to(message, text, parse_mode="HTML")

from telebot.types import Message


def help_handler(bot, message: Message):
    """
    هندلر دستور /help برای ربات تلگرام.

    پیام راهنما را با فرمت HTML برای کاربر ارسال می‌کند.
    """
    commands = [
        ("/start", "شروع کار با ربات"),
        ("/login", "ورود به حساب کاربری"),
        ("/connect", "اتصال به اینستاگرام"),
        ("/remove", "حذف حساب کاربری"),
        ("/logout", "خروج از حساب کاربری"),
        ("/account", "نمایش اطلاعات حساب کاربری"),
        ("/change_password", "تغییر رمز عبور اینستاگرام"),
        ("/analiz-follower", "تحلیل فالوورهای حساب کاربری"),  # ← اضافه شد
        ("/help", "نمایش همین راهنما"),
    ]

    text = "<b>📖 راهنمای ربات</b>\n\n<u>دستورات موجود:</u>\n\n"
    for cmd, desc in commands:
        text += f"• <code>{cmd}</code> — {desc}\n"

    bot.send_message(message.chat.id, text, parse_mode="HTML")

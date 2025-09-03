from telebot.types import Message

from bot.commands.connect import (
    get_user_from_db,
    handle_login_and_profile,
    handle_login_errors,
    send_login_stage_messages,
    setup_instagram_client,
)


def connect_instagram(bot, message: Message, proxy: str | None = None):
    """
    اتصال به حساب کاربری اینستاگرام با استفاده از اطلاعات ذخیره‌شده کاربر و ارسال پیام‌های مرحله‌ای ورود.

    Args:
        bot (TeleBot): شیء ربات تلگرام برای ارسال پیام‌ها.
        message (Message): پیام دریافتی از کاربر شامل chat_id.
        proxy (str | None): آدرس پراکسی برای اتصال به اینستاگرام (اختیاری).

    مراحل اجرا:
        1. دریافت اطلاعات کاربر از پایگاه داده.
        2. ارسال پیام‌های مرحله‌ای ورود (در صورت نیاز).
        3. راه‌اندازی کلاینت instagrapi با پراکسی.
        4. تلاش برای ورود و دریافت پروفایل کاربر.
        5. در صورت بروز خطا، مدیریت آن با ارسال پیام مناسب به کاربر.
    """
    chat_id = message.chat.id
    user = get_user_from_db(chat_id)

    if not send_login_stage_messages(bot, chat_id, user):
        return

    cl, session_file = setup_instagram_client(user, proxy)

    try:
        handle_login_and_profile(bot, chat_id, cl, user, session_file)
    except Exception as e:
        handle_login_errors(bot, chat_id, e, cl)

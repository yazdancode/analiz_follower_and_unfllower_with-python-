from telebot.types import Message

from bot.commands.connect import InstagramManager


def connect_instagram(bot, message: Message, proxy: str | None = None):
    """
    اتصال به حساب کاربری اینستاگرام با استفاده از اطلاعات ذخیره‌شده کاربر و ارسال پیام‌های مرحله‌ای ورود.
    """
    chat_id = message.chat.id
    manager = InstagramManager()

    cl, session_file, user = manager.get_user_from_db(bot, chat_id, proxy)
    if not user or not cl:
        return

    if not manager.send_login_stage_messages(bot, chat_id, user):
        return

    try:
        manager.handle_login_and_profile(bot, chat_id, cl, user, session_file)
    except Exception as e:
        manager.handle_login_errors(bot, chat_id, e, cl)

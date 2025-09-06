from bot.commands.connect import InstagramManager


def logout_handler(bot, message, proxy: str | None = None, is_action: bool = False):
    chat_id = message.chat.id
    manager = InstagramManager()

    # گرفتن کاربر و کلاینت از دیتابیس
    cl, session_file, user = manager.get_user_from_db(bot, chat_id, proxy)
    if not user or not cl:
        bot.send_message(chat_id, "❌ اتصال به اینستاگرام موفق نبود")
        return

    # انجام logout با استفاده از متد کلاس
    session_file = f"sessions/{user.username.lower()}.json"
    manager.handle_logout(bot, chat_id, user, session_file, is_action=is_action)

from telebot.types import Message

from bot.commands.connect import InstagramManager
from db.database import get_session
from db.models import User


def connect_instagram(bot, message: Message, proxy: str | None = None):
    """
    اتصال به حساب کاربری اینستاگرام با استفاده از اطلاعات ذخیره‌شده کاربر
    و ارسال پیام‌های مرحله‌ای ورود.
    """
    chat_id = message.chat.id
    manager = InstagramManager()
    cl, session_file, user = manager.get_user_from_db(bot, chat_id, proxy)
    if not user or not cl:
        return
    if not manager.send_login_stage_messages(bot, chat_id, user):
        return

    try:
        stage_result = manager.handle_login_and_profile(
            bot, chat_id, cl, user, session_file
        )
        if stage_result is None:
            with get_session() as db_session:
                db_user = db_session.get(User, user.id)
                if user.stage != "done":
                    user.stage = "done"
                    db_session.add(db_user)
                    db_session.commit()

    except Exception as e:
        manager.handle_login_errors(bot, chat_id, e, cl)

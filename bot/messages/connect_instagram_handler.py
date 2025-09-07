from telebot.types import Message

from bot.commands.connect import InstagramManager
from db.database import get_session
from db.models import User


def connect_instagram(bot, message: Message, proxy: str | None = None):
    """
    اتصال ساده به حساب کاربری اینستاگرام:
    ✅ فقط پیام موفقیت و ذخیره username در دیتابیس
    """
    chat_id = message.chat.id
    manager = InstagramManager()
    cl, session_file, user = manager.get_user_from_db(bot, chat_id, proxy)
    if not user or not cl:
        return
    if not manager.send_login_stage_messages(bot, chat_id, user):
        return

    try:
        account = cl.account_info()
        insta_username = account.username
        with get_session() as db_session:
            db_user = db_session.get(User, user.id)
            if db_user:
                db_user.stage = "done"
                db_user.username_instagram = insta_username
                db_session.commit()
        bot.send_message(
            chat_id,
            f"✅ اینستاگرام شما متصل شد!\n" f"👤 نام کاربری: <b>{insta_username}</b>",
            parse_mode="HTML",
        )

    except Exception as e:
        manager.handle_login_errors(bot, chat_id, e, cl)

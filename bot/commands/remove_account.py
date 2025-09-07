import os

from bot.commands.connect import InstagramManager
from db.database import get_session
from db.models import User


def remove_account(bot, message):
    chat_id = message.chat.id
    manager = InstagramManager()

    try:
        cl, session_file, user = manager.get_user_from_db(bot, chat_id)
        if not user:
            bot.send_message(chat_id, "❌ هیچ حسابی برای شما ثبت نشده است.")
            return
        if session_file and os.path.exists(session_file):
            os.remove(session_file)

        with get_session() as db_session:
            db_user = db_session.query(User).filter(User.chat_id == chat_id).first()
            if db_user:
                db_session.delete(db_user)
                db_session.commit()
        bot.send_message(chat_id, "✅ حساب شما با موفقیت حذف شد.")

    except Exception as e:
        bot.send_message(chat_id, f"❌ خطا در حذف حساب: {e}")

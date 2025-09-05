import os
import random
import time

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import BadPassword, LoginRequired
from sqlmodel import select

from bot.enum import BotMessages
from db.database import get_session
from db.models import User

pending_2fa = {}

load_dotenv()

ADMIN_CHAT_IDS = int(os.environ.get("ADMIN_CHAT_IDS"))


def get_user_from_db(bot, chat_id, proxy: str | None = None):
    """
    دریافت شیء کاربر از پایگاه داده بر اساس chat_id تلگرام و ورود به اینستاگرام.
    """
    with get_session() as db_session:
        user = db_session.exec(select(User).where(User.chat_id == chat_id)).first()
        print(user)
        if not user:
            bot.send_message(chat_id, BotMessages.LOGIN_REQUIRED.value)
            return

        cl, session_file = setup_instagram_client(user, proxy)
        handle_login_and_profile(bot, chat_id, cl, user, session_file, db_session)


def send_login_stage_messages(bot, chat_id, user):
    """
    بررسی وضعیت ثبت‌نام کاربر و ارسال پیام مناسب در صورت ناقص بودن اطلاعات.
    """
    if not user:
        bot.send_message(chat_id, BotMessages.LOGIN_REQUIRED.value)
        return False
    if user.stage != "done":
        bot.send_message(chat_id, BotMessages.INCOMPLETE_INFO.value)
        return False
    return True


def setup_instagram_client(user, proxy: str | None = None):
    """
    راه‌اندازی کلاینت instagrapi برای اتصال به اینستاگرام با تنظیمات کاربر.
    """
    cl = Client()

    if proxy:
        cl.set_proxy(proxy)

    os.makedirs("sessions", exist_ok=True)
    username = (user.username or f"user_{user.chat_id}").strip().lower()
    safe_username = "".join(c for c in username if c.isalnum() or c in ("_", "-"))
    session_file = f"sessions/{safe_username}.json"

    if os.path.exists(session_file):
        cl.load_settings(session_file)
    else:
        cl.dump_settings(session_file)

    return cl, session_file


def report_error_to_admin(bot, error, context=""):
    msg = f"⚠️ خطا در بخش {context}:\n{error}"
    bot.send_message(ADMIN_CHAT_IDS, msg)


def handle_login_and_profile(bot, chat_id, cl, user, session_file, db_session=None):
    """
    ورود به حساب اینستاگرام کاربر و ارسال اطلاعات پروفایل به تلگرام.
    نسخه نهایی: بررسی همه ستون‌های حیاتی قبل از commit برای جلوگیری از ROLLBACK.
    """
    try:
        cl.login(user.email, user.password)
        cl.dump_settings(session_file)

        account = cl.account_info()
        insta_username = account.username

        bot.send_message(
            chat_id, BotMessages.CONNECTED.value.format(username=insta_username)
        )

        time.sleep(random.uniform(2, 5))

        profile = cl.user_info_by_username(insta_username.lower())
        bot.send_message(
            chat_id,
            f"👤 نام کامل: {profile.full_name}\n"
            f"📸 تعداد پست‌ها: {profile.media_count}\n"
            f"👥 دنبال‌کننده‌ها: {profile.follower_count}\n"
            f"👤 دنبال‌شونده‌ها: {profile.following_count}",
        )

        # آپدیت stage کاربر
        if user.stage != "done":
            user.stage = "done"
        if not user.username_instagram:
            user.username_instagram = f"user_{user.chat_id}"

        if not user.email:
            user.email = f"user_{user.chat_id}@example.com"

        if not user.phone:
            user.phone = "0000000000"
        try:
            db_session.add(user)
            db_session.commit()
        except Exception as db_err:
            report_error_to_admin(bot, db_err, "DB commit failed ❌")
            db_session.rollback()

        time.sleep(random.uniform(10, 30))
        return None

    except BadPassword:
        bot.send_message(chat_id, BotMessages.PASSWORD_CHANGED.value)
        try:
            user.stage = "ASK_NEW_PASSWORD"
            db_session.add(user)
            db_session.commit()
        except Exception as db_err:
            report_error_to_admin(bot, db_err, "DB commit failed after BadPassword ❌")
            db_session.rollback()
        return "ASK_NEW_PASSWORD"

    except LoginRequired:
        bot.send_message(chat_id, BotMessages.LOGIN_REQUIRED.value)
        return None

    except Exception as e:
        handle_login_errors(bot, chat_id, e, cl)
        return None


def on_new_password(bot, chat_id, cl, user, session_file, db_session, password):
    """
    وقتی کاربر پسورد جدید رو فرستاد، این تابع صدا زده میشه.
    """
    try:
        cl.login(user.email, password)
        cl.dump_settings(session_file)

        # آپدیت پسورد و وضعیت
        user.password = password
        user.stage = "done"
        db_session.add(user)
        db_session.commit()

        account = cl.account_info()
        insta_username = account.username

        bot.send_message(
            chat_id, BotMessages.CONNECTED.value.format(username=insta_username)
        )

    except Exception as e:
        handle_login_errors(bot, chat_id, e, cl)


def handle_login_errors(bot, chat_id, e, cl):
    """
    مدیریت خطاهای مربوط به ورود به اینستاگرام و ارسال پیام مناسب به کاربر.
    """
    error_msg = str(e)

    if "Two-factor authentication required" in error_msg:
        bot.send_message(chat_id, BotMessages.TWO_FACTOR_REQUIRED.value)
        pending_2fa[chat_id] = cl

    elif "Facebook" in error_msg or "blacklist" in error_msg:
        bot.send_message(chat_id, BotMessages.IP_BLOCKED.value)

    else:
        bot.send_message(
            chat_id, BotMessages.CONNECT_FAILED.value.format(error=error_msg)
        )

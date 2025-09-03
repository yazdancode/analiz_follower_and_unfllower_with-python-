import os
import random
import time

from instagrapi import Client
from sqlmodel import select

from bot.enum import BotMessages
from db.database import get_session
from db.models import User

pending_2fa = {}


def get_user_from_db(chat_id):
    """
    دریافت شیء کاربر از پایگاه داده بر اساس chat_id تلگرام.

    Args:
        chat_id (int): شناسه چت کاربر در تلگرام.

    Returns:
        User | None: شیء کاربر اگر پیدا شود، در غیر این صورت None.
    """
    with get_session() as session:
        return session.exec(select(User).where(User.chat_id == chat_id)).first()


def send_login_stage_messages(bot, chat_id, user):
    """
    بررسی وضعیت ثبت‌نام کاربر و ارسال پیام مناسب در صورت ناقص بودن اطلاعات.

    Args:
        bot (TeleBot): شیء ربات تلگرام برای ارسال پیام.
        chat_id (int): شناسه چت کاربر.
        user (User | None): شیء کاربر از پایگاه داده.

    Returns:
        bool: اگر اطلاعات کاربر کامل باشد True، در غیر این صورت False.
    """
    if not user:
        bot.send_message(chat_id, BotMessages.LOGIN_REQUIRED.value)
        return False
    if user.stage != "done":
        bot.send_message(chat_id, BotMessages.INCOMPLETE_INFO.value)
        return False
    return True


def setup_instagram_client(user, proxy=None):
    """
    راه‌اندازی کلاینت instagrapi برای اتصال به اینستاگرام با تنظیمات کاربر.

    Args:
        user (User): شیء کاربر شامل اطلاعات لاگین و یوزرنیم.
        proxy (str | None): آدرس پراکسی در صورت نیاز به استفاده.

    Returns:
        tuple[Client, str]: شیء کلاینت instagrapi و مسیر فایل session مربوط به کاربر.
    """
    cl = Client()
    if proxy:
        cl.set_proxy(proxy)

    os.makedirs("sessions", exist_ok=True)
    username = user.username or f"user_{user.chat_id}"
    session_file = f"sessions/{username.lower()}.json"

    if os.path.exists(session_file):
        cl.load_settings(session_file)

    return cl, session_file


def handle_login_and_profile(bot, chat_id, cl, user, session_file):
    """
    ورود به حساب اینستاگرام کاربر و ارسال اطلاعات پروفایل به تلگرام.

    مراحل:
    - ورود به حساب با ایمیل و پسورد ذخیره‌شده
    - ذخیره تنظیمات نشست در فایل مربوطه
    - ارسال پیام اتصال موفق با یوزرنیم
    - دریافت اطلاعات پروفایل از اینستاگرام
    - ارسال جزئیات پروفایل (نام، تعداد پست، دنبال‌کننده، دنبال‌شونده)

    Args:
        bot (TeleBot): شیء ربات تلگرام برای ارسال پیام.
        chat_id (int): شناسه چت کاربر در تلگرام.
        cl (Client): کلاینت instagrapi برای اتصال به اینستاگرام.
        user (User): شیء کاربر شامل اطلاعات لاگین.
        session_file (str): مسیر فایل تنظیمات نشست برای ذخیره‌سازی.
    """
    cl.login(user.email, user.password)
    cl.dump_settings(session_file)

    bot.send_message(
        chat_id, BotMessages.CONNECTED.value.format(username=user.username)
    )

    time.sleep(random.uniform(2, 5))

    profile = cl.user_info_by_username(user.username.lower())
    bot.send_message(
        chat_id,
        f"👤 نام کامل: {profile.full_name}\n"
        f"📸 تعداد پست‌ها: {profile.media_count}\n"
        f"👥 دنبال‌کننده‌ها: {profile.follower_count}\n"
        f"👤 دنبال‌شونده‌ها: {profile.following_count}",
    )

    time.sleep(random.uniform(10, 30))


def handle_login_errors(bot, chat_id, e, cl):
    """
    مدیریت خطاهای مربوط به ورود به اینستاگرام و ارسال پیام مناسب به کاربر.

    Args:
        bot (TeleBot): شیء ربات تلگرام برای ارسال پیام.
        chat_id (int): شناسه چت کاربر در تلگرام.
        e (Exception): شیء خطا دریافت‌شده از instagrapi.
        cl (Client): کلاینت instagrapi برای ذخیره در pending_2fa در صورت نیاز.

    رفتار:
        - اگر خطا مربوط به تأیید دو مرحله‌ای باشد، پیام مناسب ارسال شده و کلاینت در pending_2fa ذخیره می‌شود.
        - اگر خطا مربوط به بلاک شدن آی‌پی یا نیاز به فیسبوک باشد، پیام راه‌حل ارسال می‌شود.
        - در سایر موارد، پیام خطای عمومی با جزئیات ارسال می‌شود.
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

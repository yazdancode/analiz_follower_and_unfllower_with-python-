import json
import logging
import os
import random
import time

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword,
    ChallengeRequired,
    LoginRequired,
    PleaseWaitFewMinutes,
    TwoFactorRequired,
)
from sqlmodel import select

from bot.enum import BotMessages
from db.database import get_session
from db.models import User

load_dotenv()
ADMIN_CHAT_IDS = [int(os.environ.get("ADMIN_CHAT_IDS"))]
logging.basicConfig(level=logging.INFO)


class InstagramManager:
    def __init__(self):
        self.pending_2fa = {}

    def get_user_from_db(self, bot, chat_id, proxy: str | None = None):
        """دریافت شیء کاربر از پایگاه داده و آماده‌سازی کلاینت اینستاگرام"""
        with get_session() as db_session:
            user = db_session.exec(
                select(User).where(User.chat_id == int(chat_id))
            ).first()
            if not user:
                bot.send_message(chat_id, BotMessages.LOGIN_REQUIRED.value)
                return None, None, None

        cl, session_file = self.setup_instagram_client(user, proxy)
        if not cl:
            bot.send_message(
                chat_id,
                BotMessages.CONNECT_FAILED.value.format(
                    error="خطا در اتصال به اینستاگرام"
                ),
            )
            return None, None, None

        return cl, session_file, user

    @staticmethod
    def setup_instagram_client(user, proxy: str | None = None):
        """راه‌اندازی کلاینت instagrapi و مدیریت session"""
        cl = Client()
        if proxy:
            cl.set_proxy(proxy)

        os.makedirs("sessions", exist_ok=True)
        safe_username = "".join(
            c
            for c in (user.username or f"user_{user.chat_id}").lower()
            if c.isalnum() or c in ("_", "-")
        )
        session_file = f"sessions/{safe_username}.json"

        try:
            if os.path.exists(session_file):
                try:
                    cl.load_settings(session_file)
                    cl.get_timeline_feed()
                except Exception:
                    os.remove(session_file)
                    logging.info(f"🗑 Session منقضی شده حذف شد: {session_file}")
                    cl = Client()
                    if proxy:
                        cl.set_proxy(proxy)
                    cl.login(user.email, user.password)
                    cl.dump_settings(session_file)
            else:
                cl.login(user.email, user.password)
                cl.dump_settings(session_file)
            return cl, session_file
        except Exception as e:
            logging.error(f"❌ خطا در setup_instagram_client: {e}")
            return None, None

    def handle_login_and_profile(self, bot, chat_id, cl, user, session_file):
        """ورود به حساب اینستاگرام و ارسال اطلاعات پروفایل"""
        try:
            cl.login(user.email, user.password)
            cl.dump_settings(session_file)

            account = cl.account_info()
            insta_username = account.username

            bot.send_message(
                chat_id, BotMessages.CONNECTED.value.format(username=insta_username)
            )

            time.sleep(random.uniform(2, 4))
            profile = cl.user_info_by_username(insta_username.lower())
            bot.send_message(
                chat_id,
                f"👤 نام کامل: {profile.full_name}\n"
                f"📸 تعداد پست‌ها: {profile.media_count}\n"
                f"👥 دنبال‌کننده‌ها: {profile.follower_count}\n"
                f"👤 دنبال‌شونده‌ها: {profile.following_count}",
            )

            # آپدیت stage و اطلاعات کاربر در session جدید
            with get_session() as db_session:
                db_user = db_session.get(User, user.id)
                if db_user:
                    db_user.stage = "done"
                    if not db_user.username_instagram:
                        db_user.username_instagram = insta_username
                    if not db_user.email:
                        db_user.email = f"user_{db_user.chat_id}@example.com"
                    if not db_user.phone:
                        db_user.phone = "0000000000"
                    db_session.commit()

            time.sleep(random.uniform(5, 10))
        except BadPassword:
            bot.send_message(chat_id, BotMessages.PASSWORD_CHANGED.value)
            with get_session() as db_session:
                db_user = db_session.get(User, user.id)
                if db_user:
                    db_user.stage = "ASK_NEW_PASSWORD"
                    db_session.commit()
        except LoginRequired:
            bot.send_message(chat_id, BotMessages.LOGIN_REQUIRED.value)
        except Exception as e:
            self.handle_login_errors(bot, chat_id, e, cl)

    def handle_login_errors(self, bot, chat_id, e, cl):
        if isinstance(e, TwoFactorRequired):
            bot.send_message(chat_id, BotMessages.TWO_FACTOR_REQUIRED.value)
            self.pending_2fa[chat_id] = cl
        elif isinstance(e, ChallengeRequired):
            bot.send_message(chat_id, BotMessages.IP_BLOCKED.value)
        elif isinstance(e, PleaseWaitFewMinutes):
            bot.send_message(chat_id, "⏳ لطفا چند دقیقه صبر کنید و دوباره تلاش کنید.")
        else:
            bot.send_message(
                chat_id, BotMessages.CONNECT_FAILED.value.format(error=str(e))
            )

    @staticmethod
    def handle_logout(bot, chat_id, user, session_file, is_action: bool = True):
        """خروج کاربر از اینستاگرام و پاکسازی session"""
        try:
            cl = Client()
            if os.path.exists(session_file):
                cl.load_settings(session_file)
                try:
                    cl.logout()
                except Exception as e:
                    bot.send_message(chat_id, f"⚠️ خطا در logout واقعی: {e}")

            # پاکسازی session و آپدیت stage با session جدید
            if is_action and os.path.exists(session_file):
                os.remove(session_file)
                with get_session() as db_session:
                    db_user = db_session.get(User, user.id)
                    if db_user:
                        db_user.stage = "logout"
                        db_session.commit()
                bot.send_message(
                    chat_id, "✅ از حساب اینستاگرام خارج شدید و session حذف شد."
                )
            else:
                bot.send_message(
                    chat_id, "✅ از حساب اینستاگرام خارج شدید (session باقی ماند)."
                )
        except Exception as e:
            bot.send_message(chat_id, f"❌ خطا در خروج: {e}")

    @staticmethod
    def send_login_stage_messages(bot, chat_id, user):
        """
        بررسی وضعیت ثبت‌نام کاربر و ارسال پیام مناسب در صورت ناقص بودن اطلاعات.
        """
        if not user:
            bot.send_message(chat_id, "❌ لطفاً ابتدا login کنید")
            return False
        if user.stage not in ["done", "logout"]:
            bot.send_message(chat_id, "❌ هنوز اطلاعات شما کامل ثبت نشده است.")
            return False
        return True

    @staticmethod
    def pending_2fa(chat_id):
        pass

    @staticmethod
    def analyze_follower(cl, chat_id, bot):
        """
        جمع‌آوری فالوورها و ذخیره در JSON با مدیریت Rate Limit اینستاگرام
        """
        try:
            username = cl.account_info().username
            if not username:
                bot.send_message(chat_id, "❌ خطا: username کاربر پیدا نشد.")
                return
            user_id = cl.user_id_from_username(username)
            followers = cl.user_followers(user_id)
            followers_data = {}
            for uname, user in followers.items():
                followers_data[uname] = {
                    "pk": user.pk,
                    "full_name": user.full_name,
                    "is_private": user.is_private,
                    "profile_pic_url": user.profile_pic_url,
                }
                time.sleep(random.uniform(0.5, 1.5))
            os.makedirs("data", exist_ok=True)
            file_path = f"data/{username}_followers.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(followers_data, f, ensure_ascii=False, indent=4)

            bot.send_message(
                chat_id, f"✅ تعداد {len(followers_data)} فالوور جمع‌آوری و ذخیره شد."
            )

        except Exception as e:
            error_msg = str(e)
            if "Please wait a few minutes" in error_msg:
                bot.send_message(
                    chat_id,
                    "⏳ اینستاگرام تعداد درخواست‌ها را محدود کرده، لطفاً چند دقیقه صبر کنید و دوباره تلاش کنید.",
                )
            else:
                bot.send_message(chat_id, f"❌ خطا در جمع‌آوری فالوورها: {error_msg}")

    @staticmethod
    def analyze_following():
        """"""
        pass

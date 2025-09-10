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
from db.models import Follower, FollowingUser, User

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
        """بررسی وضعیت ثبت‌نام کاربر و ارسال پیام مناسب در صورت ناقص بودن اطلاعات."""
        if not user:
            bot.send_message(chat_id, "❌ لطفاً ابتدا login کنید")
            return False
        if user.stage not in ["done", "logout"]:
            bot.send_message(chat_id, "❌ هنوز اطلاعات شما کامل ثبت نشده است.")
            return False
        return True

    @staticmethod
    def analyze_connections(cl, chat_id, bot, mode="followers"):
        """جمع‌آوری لیست فالوورها یا فالوئینگ‌ها و ذخیره در JSON و دیتابیس"""
        try:
            username = cl.account_info().username
            if not username:
                bot.send_message(chat_id, "❌ خطا: username کاربر پیدا نشد.")
                return

            user_id = cl.user_id_from_username(username)
            if mode == "followers":
                connections = cl.user_followers(user_id)
                label = "فالوور"
            elif mode == "following":
                connections = cl.user_following(user_id)
                label = "دنبال‌شونده"
            else:
                bot.send_message(
                    chat_id, "❌ حالت نامعتبر است (followers یا following)."
                )
                return

            connections_data = {}
            with get_session() as db_session:
                for uname, user in connections.items():
                    connections_data[uname] = {
                        "pk": user.pk,
                        "full_name": user.full_name,
                        "is_private": user.is_private,
                        "profile_pic_url": user.profile_pic_url,
                    }

                    if mode == "followers":
                        db_session.add(
                            Follower(
                                chat_id=chat_id,
                                username=uname,
                                pk=user.pk,
                                full_name=user.full_name,
                                is_private=user.is_private,
                                profile_pic_url=user.profile_pic_url,
                            )
                        )
                    else:
                        db_session.add(
                            FollowingUser(
                                chat_id=chat_id,
                                username=uname,
                                pk=user.pk,
                                full_name=user.full_name,
                                is_private=user.is_private,
                                profile_pic_url=user.profile_pic_url,
                            )
                        )
                    time.sleep(random.uniform(0.5, 1.5))

                db_session.commit()
            os.makedirs("data", exist_ok=True)
            file_path = f"data/{username}_{mode}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(connections_data, f, ensure_ascii=False, indent=4)

            bot.send_message(
                chat_id,
                f"✅ تعداد {len(connections_data)} {label} جمع‌آوری و ذخیره شد.",
            )

        except Exception as e:
            error_msg = str(e)
            if "Please wait a few minutes" in error_msg:
                bot.send_message(
                    chat_id,
                    "⏳ اینستاگرام تعداد درخواست‌ها را محدود کرده، لطفاً چند دقیقه صبر کنید و دوباره تلاش کنید.",
                )
            else:
                bot.send_message(chat_id, f"❌ خطا در جمع‌آوری {mode}: {error_msg}")

    @staticmethod
    def analyze_unfollowers_from_db(chat_id, bot):
        """بررسی آنفالو و فالو بک از دیتابیس"""
        try:
            with get_session() as db_session:
                followers = db_session.query(Follower).all()
                following = db_session.query(FollowingUser).all()

                followers_set = {f.pk for f in followers if f.pk}
                following_set = {f.pk for f in following if f.pk}

                nonfollowers = following_set - followers_set
                not_following_back = followers_set - following_set

                msg = (
                    f"📊 تحلیل دیتابیس:\n\n"
                    f"❌ کسانی که فالو کردی ولی تورو فالو نکردن: {len(nonfollowers)} نفر\n"
                    f"👤 کسانی که فالو کردن ولی فالو بک نکردی: {len(not_following_back)} نفر\n"
                    f"🤝 فالو بک کامل: {len(followers_set & following_set)} نفر"
                )
                bot.send_message(chat_id, msg)

                preview_nonfollowers = list(nonfollowers)[:10]
                preview_not_following_back = list(not_following_back)[:10]

                if preview_nonfollowers:
                    bot.send_message(
                        chat_id, f"🔻 نمونه unfollow: {preview_nonfollowers}"
                    )
                if preview_not_following_back:
                    bot.send_message(
                        chat_id,
                        f"🔻 نمونه not-following-back: {preview_not_following_back}",
                    )

        except Exception as e:
            bot.send_message(chat_id, f"❌ خطا در بررسی دیتابیس: {e}")

    @staticmethod
    def follow_nonfollowers(cl, chat_id, bot, limit: int = 10):
        """فالو بک کردن کسانی که تورو فالو کردن ولی تو هنوز فالو نکردی"""
        try:
            with get_session() as db_session:
                followers = db_session.query(Follower).all()
                following = db_session.query(FollowingUser).all()

                followers_set = {f.pk for f in followers if f.pk}
                following_set = {f.pk for f in following if f.pk}

                follow_back_candidates = list(followers_set - following_set)

                if not follow_back_candidates:
                    bot.send_message(chat_id, "✅ همه فالو بک شدن! کسی باقی نمونده.")
                    return

                success = 0
                failed = 0

                for user_pk in follow_back_candidates[:limit]:
                    try:
                        cl.user_follow(user_pk)
                        # ذخیره در دیتابیس بعد از فالو
                        db_session.add(FollowingUser(chat_id=chat_id, pk=user_pk))
                        db_session.commit()

                        success += 1
                        bot.send_message(chat_id, f"👥 فالو شد: {user_pk}")
                        time.sleep(random.uniform(3, 6))
                    except Exception as e:
                        failed += 1
                        bot.send_message(chat_id, f"⚠️ خطا در فالو {user_pk}: {e}")
                        time.sleep(random.uniform(5, 8))

                bot.send_message(
                    chat_id,
                    f"📊 عملیات فالو بک تمام شد.\n"
                    f"✅ موفق: {success}\n"
                    f"❌ ناموفق: {failed}\n"
                    f"🔢 باقی‌مانده: {len(follow_back_candidates) - success - failed}",
                )
        except Exception as e:
            bot.send_message(chat_id, f"❌ خطا در follow_nonfollowers: {e}")

    @staticmethod
    def unfollow_nonfollowers(cl, chat_id, bot, limit: int = 10):
        """
        آنفالو کردن کسانی که فالو کردی ولی تورو فالو نکردن
        limit = تعداد آنفالو در هر بار اجرا
        """
        try:
            with get_session() as db_session:
                followers = db_session.query(Follower).all()
                following = db_session.query(FollowingUser).all()

                followers_set = {f.pk for f in followers if f.pk}
                following_set = {f.pk for f in following if f.pk}
                unfollow_candidates = list(following_set - followers_set)

                if not unfollow_candidates:
                    bot.send_message(
                        chat_id, "✅ همه کسانی که فالو کردی، تورو فالو کردند!"
                    )
                    return

                success = 0
                failed = 0

                for user_pk in unfollow_candidates[:limit]:
                    try:
                        cl.user_unfollow(user_pk)
                        # حذف از دیتابیس پس از آنفالو
                        db_entry = (
                            db_session.query(FollowingUser)
                            .filter_by(pk=user_pk, chat_id=chat_id)
                            .first()
                        )
                        if db_entry:
                            db_session.delete(db_entry)
                            db_session.commit()

                        success += 1
                        bot.send_message(chat_id, f"❌ آنفالو شد: {user_pk}")
                        time.sleep(random.uniform(3, 6))  # جلوگیری از بلاک شدن
                    except Exception as e:
                        failed += 1
                        bot.send_message(chat_id, f"⚠️ خطا در آنفالو {user_pk}: {e}")
                        time.sleep(random.uniform(5, 8))

                bot.send_message(
                    chat_id,
                    f"📊 عملیات آنفالو تمام شد.\n"
                    f"✅ موفق: {success}\n"
                    f"❌ ناموفق: {failed}\n"
                    f"🔢 باقی‌مانده: {len(unfollow_candidates) - success - failed}",
                )

        except Exception as e:
            bot.send_message(chat_id, f"❌ خطا در unfollow_nonfollowers: {e}")

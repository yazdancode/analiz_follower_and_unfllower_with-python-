from telebot.types import Message

from bot.constants import BotMessages
from bot.keyboard import create_inline_keyboard


def start_handler(bot, message: Message):
    """
    هندلر دستور /start برای آغاز تعامل با ربات.

    Args:
        bot (TeleBot): شیء ربات تلگرام برای ارسال پیام.
        message (Message): پیام دریافتی از کاربر شامل chat_id.

    عملکرد:
        - ارسال پیام خوش‌آمدگویی اولیه به کاربر.
        - نمایش کیبورد خطی با دو دکمه:
            1. عضویت در کانال تلگرام
            2. تأیید عضویت
    """
    chat_id = message.chat.id
    bot.send_message(
        chat_id, BotMessages.START.value, reply_markup=create_inline_keyboard()
    )

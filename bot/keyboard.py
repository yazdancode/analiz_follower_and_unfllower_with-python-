from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_inline_keyboard():
    """
    ایجاد کیبورد خطی تلگرام برای عضویت در کانال و تأیید عضویت.

    خروجی:
        InlineKeyboardMarkup: کیبوردی شامل دو دکمه:
            - دکمه اول: لینک عضویت در کانال تلگرام.
            - دکمه دوم: دکمه تأیید عضویت با callback_data برای بررسی عضویت.
    """
    keyboard = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("عضویت در کانال 📢", url="https://t.me/yazdancodeo")
    btn2 = InlineKeyboardButton("✅ تایید عضویت", callback_data="confirm_membership")
    keyboard.add(btn1, btn2)
    return keyboard

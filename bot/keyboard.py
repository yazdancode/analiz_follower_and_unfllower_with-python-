from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("عضویت در کانال 📢", url="https://t.me/yazdancodeo")
    btn2 = InlineKeyboardButton("✅ تایید عضویت", callback_data="confirm_membership")
    keyboard.add(btn1, btn2)
    return keyboard

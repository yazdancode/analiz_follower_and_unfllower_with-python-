from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("عضویت در کانال 1 📢", url="https://t.me/YourChannel1")
    btn2 = InlineKeyboardButton("عضویت در کانال 2 🔔", url="https://t.me/YourChannel2")
    btn3 = InlineKeyboardButton("✅ تایید عضویت", callback_data="confirm_membership")
    keyboard.add(btn1)
    keyboard.add(btn2)
    keyboard.add(btn3)
    return keyboard

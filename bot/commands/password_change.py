from bot.enum import BotMessages
from bot.messages.login_handler import get_user


# مرحله 1: درخواست پسورد جدید
def change_password_request(bot, message):
    chat_id = message.chat.id
    user, session = get_user(chat_id)
    if not user:
        bot.send_message(chat_id, BotMessages.USER_NOT_FOUND.value)
        return

    bot.send_message(chat_id, "📝 لطفاً پسورد جدید خود را وارد کنید.\n")
    user.stage = "waiting_new_password"
    session.add(user)
    session.commit()


def update_password(bot, message):
    chat_id = message.chat.id
    text = message.text.strip()

    user, session = get_user(chat_id)
    if not user:
        bot.send_message(chat_id, BotMessages.USER_NOT_FOUND.value)
        return

    if user.stage != "waiting_new_password":
        bot.send_message(chat_id, "❌ لطفاً ابتدا دستور /change_password را ارسال کنید.")
        return
    if len(text) > 15:
        bot.send_message(chat_id, BotMessages.PASSWORD_TOO_SHORT.value)
        return
    if not any(c.islower() for c in text):
        bot.send_message(chat_id, BotMessages.PASSWORD_NO_LOWERCASE.value)
        return
    if not any(c.isdigit() for c in text):
        bot.send_message(chat_id, BotMessages.PASSWORD_NO_DIGIT.value)
        return
    user.password = text
    user.stage = "done"
    session.add(user)
    session.commit()

    bot.send_message(chat_id, "✅ پسورد شما با موفقیت تغییر کرد!")

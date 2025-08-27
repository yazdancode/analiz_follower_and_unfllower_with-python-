import telebot
from decouple import config
from telebot.types import Message
from Enum import enum
from keyboard.keybord import create_inline_keyboard

TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)


def start_bot():
    @bot.message_handler(commands=["start"])
    def start_handler(message: Message):
        bot.send_message(
            message.chat.id, enum.message_start(), reply_markup=create_inline_keyboard()
        )

    @bot.callback_query_handler(func=lambda call: call.data == "confirm_membership")
    def confirm_handler(call):
        bot.answer_callback_query(call.id, "🔎 در حال بررسی عضویت شما...")
        bot.send_message(call.message.chat.id, "✅ عضویت شما تایید شد!")


def initialize_bot() -> None:
    start_bot()


if __name__ == "__main__":
    initialize_bot()
    bot.polling(none_stop=True)

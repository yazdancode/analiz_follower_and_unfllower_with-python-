from telebot import TeleBot
from telebot.types import Message
from bot.keyboard import create_inline_keyboard
from bot.enum import BotMessages
from bot.callbacks.membership import confirm_membership

def register_handlers(bot: TeleBot):

    @bot.message_handler(commands=["start"])
    def start_handler(message: Message):
        chat_id = message.chat.id
        bot.send_message(
            chat_id,
            BotMessages.START.value,
            reply_markup=create_inline_keyboard()
        )
    @bot.callback_query_handler(func=lambda call: call.data == "confirm_membership")
    def confirm_membership_handler(call):
        confirm_membership(bot, call)

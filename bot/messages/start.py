from telebot.types import Message
from bot.keyboard import create_inline_keyboard
from bot.enum import BotMessages

def start_handler(bot, message: Message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        BotMessages.START.value,
        reply_markup=create_inline_keyboard()
    )

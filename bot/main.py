from decouple import config
from telebot import TeleBot

from bot.handlers import register_handlers

BOT_TOKEN = config("TELEGRAM_TOKEN")
bot = TeleBot(BOT_TOKEN)

register_handlers(bot)

print("Bot is running...")
bot.infinity_polling()

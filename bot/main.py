import telebot
from decouple import config
from db.database import init_db
from bot.handlers import register_handlers

TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

init_db()
register_handlers(bot)

if __name__ == "__main__":
    bot.polling(none_stop=True)

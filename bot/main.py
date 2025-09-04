from decouple import config
from telebot import TeleBot

from bot.commands.bot_commands import set_bot_commands
from bot.handlers import register_handlers
from db.database import create_db_and_tables

BOT_TOKEN = config("TELEGRAM_TOKEN")
bot = TeleBot(BOT_TOKEN)
set_bot_commands(bot)
register_handlers(bot)

if __name__ == "__main__":
    print("Bot is running...")
    create_db_and_tables()
    bot.infinity_polling()

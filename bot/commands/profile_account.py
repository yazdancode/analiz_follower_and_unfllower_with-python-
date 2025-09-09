from bot.commands.connect import InstagramManager


def profile(bot, message):
    chat_id = message.chat.id
    manager = InstagramManager()
    cl, session_file, user = manager.get_user_from_db(bot, chat_id)

    if not cl or not user:
        return
    manager.handle_login_and_profile(bot, chat_id, cl, user, session_file)


def analyze_command(message, bot):
    pass

import logging
import sys
from telebot.types import BotCommand
from src.utils.logging import setup_logging
from src.config import settings
from src.loader import bot
from src.db.migrations import apply_migrations

import src.handlers

if sys.version_info < (3, 12):
    current_version = ".".join(map(str, sys.version_info[:3]))
    error_message = "This project requires Python 3.12.0 or higher. You are using Python {current_version}".format(current_version=current_version)
    raise RuntimeError(error_message)


def register_commands():
    commands = [
        BotCommand(command="start", description="Start interaction with the bot"),
        BotCommand(command="help", description="Get help information"),
        BotCommand(command="catalog", description="Browse the product catalog"),
    ]
    bot.set_my_commands(commands)


def main():
    apply_migrations()

    setup_logging()
    register_commands()
    logging.getLogger(__name__).info("Bot starting with long polling...")
    bot.infinity_polling(
        skip_pending=settings.skip_pending,
        timeout=settings.long_polling_timeout,
        long_polling_timeout=settings.long_polling_timeout,
        allowed_updates=["message", "callback_query"]
    )


if __name__ == "__main__":
    main()

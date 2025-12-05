import asyncio
import logging
import sys

from telebot.types import BotCommand

from src.config import settings
from src.constants import (
    ADD_PRODUCT_CMD,
    ADMIN_CMD,
    CATALOG_CMD,
    FEEDBACK_CMD,
    HELP_CMD,
    LANGUAGE_CMD,
    REMOVE_PRODUCT_CMD,
    START_CMD,
    VIEW_ALL_ORDERS_CMD,
)
from src.db.migrations import apply_migrations
from src.loader import bot
from src.middlewares import LanguageMiddleware, LoggingMiddleware
from src.utils.logging import setup_logging
import src.handlers  # noqa: F401

if sys.version_info < (3, 12):
    current_version = ".".join(map(str, sys.version_info[:3]))
    error_message = "This project requires Python 3.12.0 or higher. You are using Python {current_version}".format(
        current_version=current_version
    )
    raise RuntimeError(error_message)


async def register_commands():
    commands = [
        BotCommand(command=START_CMD, description="Start interaction with the bot"),
        BotCommand(command=HELP_CMD, description="Get help information"),
        BotCommand(command=CATALOG_CMD, description="Browse the product catalog"),
        BotCommand(command=ADMIN_CMD, description="Browse the product catalog"),
        BotCommand(command=VIEW_ALL_ORDERS_CMD, description="View all pending orders"),
        BotCommand(
            command=ADD_PRODUCT_CMD, description="Add a new product to the catalog"
        ),
        BotCommand(
            command=REMOVE_PRODUCT_CMD, description="Remove a product from the catalog"
        ),
        BotCommand(command=FEEDBACK_CMD, description="Send feedback about the bot"),
        BotCommand(command=LANGUAGE_CMD, description="Change language"),
    ]
    await bot.set_my_commands(commands)


async def main():
    setup_logging()
    await apply_migrations()

    bot.setup_middleware(LoggingMiddleware())
    bot.setup_middleware(LanguageMiddleware())
    await register_commands()
    logging.getLogger(__name__).info("Bot starting with long polling...")
    await bot.infinity_polling(
        skip_pending=settings.skip_pending,
        timeout=settings.long_polling_timeout,
        allowed_updates=["message", "callback_query"],
    )


if __name__ == "__main__":
    asyncio.run(main())

import logging
import sys
import asyncio
from telebot.types import BotCommand
from src.utils.logging import setup_logging
from src.config import settings
from src.loader import bot
from src.db.migrations import apply_migrations
from src.constants import CATALOG_CMD, START_CMD, ADMIN_CMD, HELP_CMD, VIEW_ALL_ORDERS_CMD, ADD_PRODUCT_CMD, REMOVE_PRODUCT_CMD

import src.handlers

if sys.version_info < (3, 12):
    current_version = ".".join(map(str, sys.version_info[:3]))
    error_message = "This project requires Python 3.12.0 or higher. You are using Python {current_version}".format(current_version=current_version)
    raise RuntimeError(error_message)


async def register_commands():
    commands = [
        BotCommand(command=START_CMD, description="Start interaction with the bot"),
        BotCommand(command=HELP_CMD, description="Get help information"),
        BotCommand(command=CATALOG_CMD, description="Browse the product catalog"),
        BotCommand(command=ADMIN_CMD, description="Browse the product catalog"),
        BotCommand(command=VIEW_ALL_ORDERS_CMD, description="View all pending orders"),
        BotCommand(command=ADD_PRODUCT_CMD, description="Add a new product to the catalog"),
        BotCommand(command=REMOVE_PRODUCT_CMD, description="Remove a product from the catalog"),
    ]
    await bot.set_my_commands(commands)


async def main():
    await apply_migrations()

    setup_logging()
    await register_commands()
    logging.getLogger(__name__).info("Bot starting with long polling...")
    await bot.infinity_polling(
        skip_pending=settings.skip_pending,
        timeout=settings.long_polling_timeout,
        allowed_updates=["message", "callback_query"]
    )


if __name__ == "__main__":
    asyncio.run(main())

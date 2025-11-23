from telebot import asyncio_filters
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage

from .config import settings

state_storage = StateMemoryStorage()
bot = AsyncTeleBot(
    settings.bot_token, state_storage=state_storage, parse_mode=settings.parse_mode
)

bot.add_custom_filter(asyncio_filters.StateFilter(bot))

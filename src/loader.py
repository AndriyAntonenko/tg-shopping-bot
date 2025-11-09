from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from telebot.custom_filters import StateFilter
from .config import settings

state_storage = StateMemoryStorage()
bot = TeleBot(settings.bot_token, state_storage=state_storage, parse_mode=settings.parse_mode)

bot.add_custom_filter(StateFilter(bot))

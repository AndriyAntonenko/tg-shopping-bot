from telebot.types import Message

from src.loader import bot
from src.resources.strings import get_string


@bot.message_handler(func=lambda message: True, content_types=["text"])
async def handle_unmatched_message(message: Message):
    """
    Catch-all handler for messages that didn't match any other handler.
    """
    response_key = "fallback_message"
    lang_code = getattr(message, "language_code", "en")
    response = get_string(response_key, lang_code)
    await bot.reply_to(message, response)

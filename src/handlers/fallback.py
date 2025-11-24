from telebot.types import Message

from src.loader import bot


@bot.message_handler(func=lambda message: True, content_types=["text"])
async def handle_unmatched_message(message: Message):
    """
    Catch-all handler for messages that didn't match any other handler.
    """
    response = (
        "I'm not sure how to help with that, but I'm learning! 🤖\n\n"
        "Try using /help to see what I can do, or check out our /catalog."
    )
    await bot.reply_to(message, response)

import logging
from telebot.asyncio_handler_backends import BaseMiddleware, CancelUpdate
from telebot.types import CallbackQuery

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ["message", "callback_query"]

    async def pre_process(self, message_or_callback_query, data):
        if isinstance(message_or_callback_query, CallbackQuery):
            user = message_or_callback_query.from_user
            logger.info(
                f"Received callback query from {user.username} ({user.id}): {message_or_callback_query.data}"
            )
        else:
            user = message_or_callback_query.from_user
            if message_or_callback_query.content_type == "text":
                logger.info(
                    f"Received message from {user.username} ({user.id}): {message_or_callback_query.text}"
                )
            elif message_or_callback_query.content_type == "photo":
                logger.info(f"Received photo from {user.username} ({user.id})")
            else:
                logger.info(
                    f"Received update ({message_or_callback_query.content_type}) from {user.username} ({user.id})"
                )

    async def post_process(self, message_or_callback_query, data, exception):
        if exception:
            logger.error(f"Error processing update: {exception}")

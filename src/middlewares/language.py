from telebot.asyncio_handler_backends import BaseMiddleware

from ..services.users import UsersService


class LanguageMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ["message", "callback_query"]
        self.users_service = UsersService()

    async def pre_process(self, message_or_callback_query, data):
        user_id = message_or_callback_query.from_user.id
        user = await self.users_service.get_user_if_exists(user_id)

        language_code = "en"
        if user and user.language_code:
            language_code = user.language_code

        # Attach language_code to the object
        message_or_callback_query.language_code = language_code

    async def post_process(self, message_or_callback_query, data, exception):
        pass

from functools import wraps

from telebot.types import CallbackQuery

from ..loader import bot
from ..services.users import UsersService


def admin_guard(func):
    users_service = UsersService()

    @wraps(func)
    async def wrapper(call_or_message, *args, **kwargs):
        tg_user_id = call_or_message.from_user.id
        chat_id = (
            call_or_message.message.chat.id
            if isinstance(call_or_message, CallbackQuery)
            else call_or_message.chat.id
        )
        user = await users_service.get_user_if_exists(tg_user_id)
        if user is None or not user.is_admin:
            await bot.send_message(
                chat_id, "🚫 You do not have permission to access admin commands."
            )
            return
        return await func(call_or_message, *args, **kwargs)

    return wrapper

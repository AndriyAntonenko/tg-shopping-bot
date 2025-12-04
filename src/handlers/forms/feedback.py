from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import Message

from ...constants import FEEDBACK_CMD
from ...loader import bot
from ...resources.strings import get_string
from ...services.feedback import FeedbackService
from ...services.users import UsersService


class FeedbackState(StatesGroup):
    waiting_for_feedback = State()


@bot.message_handler(commands=[FEEDBACK_CMD])
async def cmd_feedback(message: Message):
    lang_code = getattr(message, "language_code", "en")
    await bot.set_state(
        message.from_user.id, FeedbackState.waiting_for_feedback, message.chat.id
    )
    await bot.send_message(
        message.chat.id,
        get_string("enter_feedback", lang_code),
    )


@bot.message_handler(
    func=lambda message: message.text
    in [get_string("feedback", "en"), get_string("feedback", "uk")]
)
async def handle_feedback(message: Message):
    lang_code = getattr(message, "language_code", "en")
    await bot.set_state(
        message.from_user.id, FeedbackState.waiting_for_feedback, message.chat.id
    )
    await bot.send_message(
        message.chat.id,
        get_string("enter_feedback", lang_code),
    )


@bot.message_handler(state=FeedbackState.waiting_for_feedback)
async def handle_feedback_message(message: Message):
    feedback_text = message.text
    user_id = message.from_user.id
    username = message.from_user.username

    # Save feedback
    feedback_service = FeedbackService()
    users_service = UsersService()

    # We need the internal user ID for the database, not the Telegram ID
    user = await users_service.get_user_if_exists(user_id)
    if user:
        await feedback_service.create_feedback(user.id, feedback_text)

        # Notify admins
        admins = await users_service.get_admins()
        for admin in admins:
            try:
                await bot.send_message(
                    admin.telegram_user_id,
                    f"New feedback from @{username} (ID: {user_id}):\n\n{feedback_text}",
                )
            except Exception as e:
                print(f"Failed to send feedback to admin {admin.telegram_user_id}: {e}")

    lang_code = getattr(message, "language_code", "en")
    await bot.send_message(
        message.chat.id,
        get_string("feedback_sent", lang_code),
    )
    await bot.delete_state(message.from_user.id, message.chat.id)

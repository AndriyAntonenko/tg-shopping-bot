from telebot.types import CallbackQuery

from ..constants import CHECK_PAYMENT_CQ_PREFIX
from ..loader import bot
from .common import check_payment_logic


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(CHECK_PAYMENT_CQ_PREFIX)
)
async def handle_check_payment(call: CallbackQuery):
    order_id_str = call.data.removeprefix(CHECK_PAYMENT_CQ_PREFIX)
    if not order_id_str.isdigit():
        await bot.answer_callback_query(call.id, "Invalid order ID.")
        return

    lang_code = getattr(call, "language_code", "en")
    await check_payment_logic(
        message_chat_id=call.message.chat.id,
        user_id=call.from_user.id,
        order_id=int(order_id_str),
        callback_query_id=call.id,
        lang_code=lang_code,
    )

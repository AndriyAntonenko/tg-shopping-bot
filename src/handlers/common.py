
from ..loader import bot
from ..resources.strings import get_string
from ..services.orders import OrdersService, OrderStatus
from ..services.payments import PaymentService


async def check_payment_logic(
    message_chat_id: int,
    user_id: int,
    order_id: int,
    callback_query_id: str = None,
    lang_code: str = "en",
):
    orders_service = OrdersService()
    payment_service = PaymentService()

    order = await orders_service.get_order_by_id(order_id)
    if not order:
        msg = get_string("order_not_found", lang_code)
        if callback_query_id:
            await bot.answer_callback_query(callback_query_id, msg)
        else:
            await bot.send_message(message_chat_id, msg)
        return

    if order.status == OrderStatus.PAID.value:
        msg = get_string("order_already_paid", lang_code)
        if callback_query_id:
            await bot.answer_callback_query(callback_query_id, msg)
        else:
            await bot.send_message(message_chat_id, msg)
        return

    if not order.stripe_session_id:
        msg = get_string("no_payment_info", lang_code)
        if callback_query_id:
            await bot.answer_callback_query(callback_query_id, msg)
        else:
            await bot.send_message(message_chat_id, msg)
        return

    try:
        status = await payment_service.check_payment_status(order.stripe_session_id)

        if status == "paid":
            await orders_service.update_order_status(order.id, OrderStatus.PAID)
            success_msg = get_string("payment_successful", lang_code)
            if callback_query_id:
                await bot.answer_callback_query(callback_query_id, success_msg)

            await bot.send_message(
                message_chat_id,
                get_string("payment_received", lang_code).format(order_id=order.id),
            )
        else:
            status_msg = get_string("payment_status", lang_code).format(status=status)
            if callback_query_id:
                await bot.answer_callback_query(callback_query_id, status_msg)
            else:
                await bot.send_message(message_chat_id, status_msg)

    except Exception:
        err_msg = get_string("error_check_payment", lang_code)
        if callback_query_id:
            await bot.answer_callback_query(callback_query_id, err_msg)
        else:
            await bot.send_message(message_chat_id, err_msg)

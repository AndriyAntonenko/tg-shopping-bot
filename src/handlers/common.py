from telebot.types import CallbackQuery

from ..constants import CHECK_PAYMENT_CQ_PREFIX
from ..loader import bot
from ..services.orders import OrdersService, OrderStatus
from ..services.payments import PaymentService

async def check_payment_logic(message_chat_id: int, user_id: int, order_id: int, callback_query_id: str = None):
  orders_service = OrdersService()
  payment_service = PaymentService()

  order = await orders_service.get_order_by_id(order_id)
  if not order:
      msg = "Order not found."
      if callback_query_id:
          await bot.answer_callback_query(callback_query_id, msg)
      else:
          await bot.send_message(message_chat_id, msg)
      return

  if order.status == OrderStatus.PAID.value:
      msg = "Order is already paid! ✅"
      if callback_query_id:
          await bot.answer_callback_query(callback_query_id, msg)
      else:
          await bot.send_message(message_chat_id, msg)
      return

  if not order.stripe_session_id:
      msg = "No payment info found for this order."
      if callback_query_id:
          await bot.answer_callback_query(callback_query_id, msg)
      else:
          await bot.send_message(message_chat_id, msg)
      return

  try:
      status = await payment_service.check_payment_status(order.stripe_session_id)

      if status == "paid":
          await orders_service.update_order_status(order.id, OrderStatus.PAID)
          success_msg = "Payment successful! ✅"
          if callback_query_id:
              await bot.answer_callback_query(callback_query_id, success_msg)
          
          await bot.send_message(
              message_chat_id,
              f"Payment received for Order #{order.id}! Thank you! 🎉\nWe will process it shortly."
          )
      else:
          status_msg = f"Payment status: {status}. Please complete payment."
          if callback_query_id:
              await bot.answer_callback_query(callback_query_id, status_msg)
          else:
              await bot.send_message(message_chat_id, status_msg)

  except Exception:
      err_msg = "Error checking payment status."
      if callback_query_id:
          await bot.answer_callback_query(callback_query_id, err_msg)
      else:
          await bot.send_message(message_chat_id, err_msg)

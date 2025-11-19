from telebot.types import Message
from ..loader import bot

from ..services.users import UsersService, User
from ..keyboards.inline import admin_keyboard, pending_orders_keyboard, admin_order_commands_keyboard
from ..services.orders import OrdersService, OrderStatus
from ..constants import VIEW_PENDING_ORDERS_CQ, VIEW_ORDER_DETAILS_CQ_PREFIX, ADMIN_CMD, APPROVE_ORDER_CQ_PREFIX, CANCEL_ORDER_CQ_PREFIX

async def check_admin(user_id: int) -> User | None:
  users_service = UsersService()
  user = await users_service.get_user_if_exists(user_id)
  return user is not None and user

async def send_admin_guard_message(chat_id):
  await bot.send_message(chat_id, "🚫 You do not have permission to access admin commands.")

@bot.message_handler(commands=[ADMIN_CMD])
async def cmd_admin(message: Message):
  admin = await check_admin(message.from_user.id);
  if not admin:
    await send_admin_guard_message(message)
    return
  
  await bot.send_message(message.chat.id, '''Hello @{username}!
Welcome to the admin panel. Use the buttons below to manage pending orders.'''.format(username=message.from_user.username),
                   reply_markup=admin_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == VIEW_PENDING_ORDERS_CQ)
async def handle_view_pending_orders(call):
  admin = await check_admin(call.from_user.id);
  if not admin:
    await send_admin_guard_message(call.message.chat.id)
    return
  
  orders_service = OrdersService()
  pending_orders_count = await orders_service.get_pending_orders_count()
  if pending_orders_count == 0:
    await bot.answer_callback_query(call.id, "There are no pending orders at the moment.")

  pending_orders = await orders_service.get_pending_orders_list(None)
  msg = "You have {count} pending orders.\n\nClick the button below to check order details".format(count=pending_orders_count)
  await bot.send_message(call.message.chat.id, msg, reply_markup=pending_orders_keyboard(pending_orders))
  

@bot.callback_query_handler(func=lambda call: call.data.startswith(VIEW_ORDER_DETAILS_CQ_PREFIX))
async def handle_order_details(call):
  admin = await check_admin(call.from_user.id);
  if not admin:
    await send_admin_guard_message(call.message.chat.id)
    return
  
  order_id_str = call.data.removeprefix(VIEW_ORDER_DETAILS_CQ_PREFIX)
  order_id = int(order_id_str) if order_id_str.isdigit() else 0
  if order_id == 0:
    await bot.answer_callback_query(call.id, "Invalid order ID.")
    return
  
  orders_service = OrdersService()
  orders = await orders_service.get_pending_orders_list([order_id])
  if len(orders) == 0:
    await bot.answer_callback_query(call.id, "Order not found.")
    return
  order = orders[0]
  msg = f'''Order Details:\n
Order ID: {order.id}
Product: {order.product_name}
Price: {order.product_price} {order.product_currency}
Ordered by: @{order.user_telegram_username} (User ID: {order.user_telegram_user_id})
Status: {order.status.name}
Created At: {order.created_at}'''
  
  await bot.send_message(call.message.chat.id, msg, reply_markup=admin_order_commands_keyboard(order.id))

@bot.callback_query_handler(func=lambda call: call.data.startswith(APPROVE_ORDER_CQ_PREFIX))
async def handle_approve_order(call):
  admin = await check_admin(call.from_user.id);
  if not admin:
    await send_admin_guard_message(call.message.chat.id)
    return
  
  order_id_str = call.data.removeprefix(APPROVE_ORDER_CQ_PREFIX)
  order_id = int(order_id_str) if order_id_str.isdigit() else 0
  if order_id == 0:
    await bot.answer_callback_query(call.id, "Invalid order ID.")
    return
  
  orders_service = OrdersService()
  success = await orders_service.update_order_status(order_id, OrderStatus.COMPLETED)
  if not success:
    await bot.answer_callback_query(call.id, "Failed to approve order. It may not exist or is not pending.")
    return
  
  await bot.answer_callback_query(call.id, f"Order #{order_id} has been approved.")
  await bot.send_message(call.message.chat.id, f"Order #{order_id} has been marked as completed.", reply_markup=admin_keyboard())  

@bot.callback_query_handler(func=lambda call: call.data.startswith(CANCEL_ORDER_CQ_PREFIX))
async def handle_cancel_order(call):
  admin = await check_admin(call.from_user.id);
  if not admin:
    await send_admin_guard_message(call.message.chat.id)
    return
  
  order_id_str = call.data.removeprefix(CANCEL_ORDER_CQ_PREFIX)
  order_id = int(order_id_str) if order_id_str.isdigit() else 0
  if order_id == 0:
    await bot.answer_callback_query(call.id, "Invalid order ID.")
    return
  
  orders_service = OrdersService()
  success = await orders_service.update_order_status(order_id, OrderStatus.CANCELED)
  if not success:
    await bot.answer_callback_query(call.id, "Failed to cancel order. It may not exist or is not pending.")
    return
  
  await bot.answer_callback_query(call.id, f"Order #{order_id} has been canceled.")
  await bot.send_message(call.message.chat.id, f"Order #{order_id} has been marked as canceled.", reply_markup=admin_keyboard())

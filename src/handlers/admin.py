from telebot.types import Message

from ..constants import (
    ADMIN_CMD,
    APPROVE_ORDER_CQ_PREFIX,
    CANCEL_ORDER_CQ_PREFIX,
    VIEW_ALL_ORDERS_CMD,
    VIEW_ORDER_DETAILS_CQ_PREFIX,
    VIEW_PENDING_ORDERS_CQ,
    REMOVE_PRODUCT_PREFIX,
    REMOVE_PRODUCT_CMD,
    CONFIRM_REMOVE_PRODUCT_PREFIX,
    CANCEL_REMOVE_PRODUCT_PREFIX,
    REMOVE_PRODUCT_CURSOR_PREFIX,
    VIEW_FEEDBACKS_CQ_PREFIX,
    VIEW_FEEDBACK_DETAILS_CQ_PREFIX,
)
from ..guards.admin import admin_guard
from ..keyboards.inline import (
    admin_keyboard,
    admin_order_commands_keyboard,
    pending_orders_keyboard,
    admin_remove_products_keyboard,
    admin_remove_products_keyboard,
    confirm_remove_product_keyboard,
    feedbacks_list_keyboard,
    feedback_details_keyboard,
)
from ..loader import bot
from ..services.feedback import FeedbackService
from ..services.orders import OrdersService, OrderStatus
from ..services.products import GetProductsListParams, ProductService
from ..services.storage import StorageService


@bot.message_handler(commands=[ADMIN_CMD])
@admin_guard
async def cmd_admin(message: Message):
    await bot.send_message(
        message.chat.id,
        """Hello @{username}!
Welcome to the admin panel. Use the buttons below to manage pending orders.""".format(
            username=message.from_user.username
        ),
        reply_markup=admin_keyboard(),
    )


@bot.message_handler(commands=[VIEW_ALL_ORDERS_CMD])
@admin_guard
async def cmd_view_all_orders(message: Message):
    orders_service = OrdersService()
    pending_orders_count = await orders_service.get_pending_orders_count()
    if pending_orders_count == 0:
        await bot.answer_callback_query(
            message.id, "There are no pending orders at the moment."
        )
        await bot.send_message(
            message.chat.id,
            "There are no pending orders at the moment.",
        )
        return

    pending_orders = await orders_service.get_pending_orders_list(None)
    msg = "You have {count} pending orders.\n\nClick the button below to check order details".format(
        count=pending_orders_count
    )
    await bot.send_message(
        message.chat.id,
        msg,
        reply_markup=pending_orders_keyboard(pending_orders),
    )


@bot.callback_query_handler(func=lambda call: call.data == VIEW_PENDING_ORDERS_CQ)
@admin_guard
async def handle_view_pending_orders(call):
    orders_service = OrdersService()
    pending_orders_count = await orders_service.get_pending_orders_count()
    if pending_orders_count == 0:
        await bot.answer_callback_query(
            call.id, "There are no pending orders at the moment."
        )
        await bot.send_message(
            call.message.chat.id,
            "There are no pending orders at the moment.",
        )
        return

    pending_orders = await orders_service.get_pending_orders_list(None)
    msg = "You have {count} pending orders.\n\nClick the button below to check order details".format(
        count=pending_orders_count
    )
    await bot.send_message(
        call.message.chat.id, msg, reply_markup=pending_orders_keyboard(pending_orders)
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(VIEW_ORDER_DETAILS_CQ_PREFIX)
)
@admin_guard
async def handle_order_details(call):
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
    msg = f"""Order Details:\n
Order ID: {order.id}
Product: {order.product_name}
Price: {order.product_price} {order.product_currency}
Ordered by: @{order.user_telegram_username} (User ID: {order.user_telegram_user_id})
Status: {order.status.name}
Created At: {order.created_at}"""

    await bot.send_message(
        call.message.chat.id, msg, reply_markup=admin_order_commands_keyboard(order.id)
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(APPROVE_ORDER_CQ_PREFIX)
)
@admin_guard
async def handle_approve_order(call):
    order_id_str = call.data.removeprefix(APPROVE_ORDER_CQ_PREFIX)
    order_id = int(order_id_str) if order_id_str.isdigit() else 0
    if order_id == 0:
        await bot.answer_callback_query(call.id, "Invalid order ID.")
        return

    orders_service = OrdersService()
    success = await orders_service.update_order_status(order_id, OrderStatus.COMPLETED)
    if not success:
        await bot.answer_callback_query(
            call.id, "Failed to approve order. It may not exist or is not pending."
        )
        return

    await bot.answer_callback_query(call.id, f"Order #{order_id} has been approved.")
    await bot.send_message(
        call.message.chat.id,
        f"Order #{order_id} has been marked as completed.",
        reply_markup=admin_keyboard(),
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(CANCEL_ORDER_CQ_PREFIX)
)
@admin_guard
async def handle_cancel_order(call):
    order_id_str = call.data.removeprefix(CANCEL_ORDER_CQ_PREFIX)
    order_id = int(order_id_str) if order_id_str.isdigit() else 0
    if order_id == 0:
        await bot.answer_callback_query(call.id, "Invalid order ID.")
        return

    orders_service = OrdersService()
    success = await orders_service.update_order_status(order_id, OrderStatus.CANCELED)
    if not success:
        await bot.answer_callback_query(
            call.id, "Failed to cancel order. It may not exist or is not pending."
        )
        return

    await bot.answer_callback_query(call.id, f"Order #{order_id} has been canceled.")
    await bot.send_message(
        call.message.chat.id,
        f"Order #{order_id} has been marked as canceled.",
        reply_markup=admin_keyboard(),
    )


@bot.message_handler(commands=[REMOVE_PRODUCT_CMD])
@admin_guard
async def cmd_remove_product(message):
    await show_products_to_remove(message.chat.id, 0)


async def show_products_to_remove(chat_id, cursor):
    product_service = ProductService()
    params = GetProductsListParams(limit=6, cursor=cursor, sort_desc=True)
    products, next_cursor = await product_service.get_products_list(params)

    if not products:
        await bot.send_message(chat_id, "No products available to remove.")
        return

    markup = admin_remove_products_keyboard(products, next_cursor)
    await bot.send_message(chat_id, "Select a product to remove:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith(REMOVE_PRODUCT_CURSOR_PREFIX))
async def handle_remove_pagination(call):
    cursor = call.data.removeprefix(REMOVE_PRODUCT_CURSOR_PREFIX)
    cursor = int(cursor) if cursor.isdigit() else 0
    if cursor == 0:
        await bot.answer_callback_query(call.id, "Invalid cursor.")
        return
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await show_products_to_remove(call.message.chat.id, cursor)


@bot.callback_query_handler(func=lambda call: call.data.startswith(REMOVE_PRODUCT_PREFIX))
async def handle_product_selection(call):
    product_id = int(call.data.removeprefix(REMOVE_PRODUCT_PREFIX))
    if product_id == 0:
        await bot.answer_callback_query(call.id, "Invalid product ID.")
        return
    product_service = ProductService()
    product = await product_service.get_product_by_id(product_id)

    if not product:
        await bot.answer_callback_query(call.id, "Product not found.")
        return

    caption = (
        f"Are you sure you want to remove this product?\n\n"
        f"Name: {product.name}\n"
        f"Description: {product.description}\n"
        f"Price: {product.price} {product.currency}"
    )

    markup = confirm_remove_product_keyboard(product_id)

    if product.image_url:
        await bot.send_photo(
            call.message.chat.id, product.image_url, caption=caption, reply_markup=markup
        )
    else:
        await bot.send_message(call.message.chat.id, caption, reply_markup=markup)
    
    await bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith(CANCEL_REMOVE_PRODUCT_PREFIX))
async def handle_cancel_remove(call):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.send_message(call.message.chat.id, "Removal canceled.")
    await show_products_to_remove(call.message.chat.id, 0)


@bot.callback_query_handler(func=lambda call: call.data.startswith(CONFIRM_REMOVE_PRODUCT_PREFIX))
async def handle_confirm_remove(call):
    product_id = int(call.data.removeprefix(CONFIRM_REMOVE_PRODUCT_PREFIX))
    product_service = ProductService()
    storage_service = StorageService()

    product = await product_service.get_product_by_id(product_id)
    if not product:
        await bot.answer_callback_query(call.id, "Product not found.")
        return

    # Delete image if exists
    if product.image_url:
        # Extract file name from URL or store it differently? 
        # The URL is https://{bucket}.{region}.cdn.digitaloceanspaces.com/{bucket}/{file_name}
        # We need just the file_name (key).
        # Based on storage.py: url = f"https://{self.bucket}.{self.region}.cdn.digitaloceanspaces.com/{self.bucket}/{file_name}"
        # So we can split by / and take the last part? 
        # Wait, the URL construction in storage.py is:
        # url = f"https://{self.bucket}.{self.region}.cdn.digitaloceanspaces.com/{self.bucket}/{file_name}"
        # So yes, the last part is the file name.
        # However, let's be safer.
        
        try:
            file_name = product.image_url.split("/")[-1]
            # Also need to handle if there are folders in the key like "products/uuid.ext"
            # In add_product.py: file_name = f"products/{uuid.uuid4()}.{file_ext}"
            # So the URL will end with products/uuid.ext
            # Let's check the URL structure again.
            # https://bucket.region.cdn.../bucket/products/uuid.ext
            # So splitting by / might give uuid.ext, but we need products/uuid.ext?
            # Let's look at storage.py again.
            # Key=file_name
            # url = .../{self.bucket}/{file_name}
            # So if file_name is "products/foo.jpg", url ends with /bucket/products/foo.jpg
            # So we need to extract everything after /bucket/
            
            # A safer way might be to store the key in the DB, but we don't have that column.
            # We have to parse the URL.
            from src.config import settings
            bucket_part = f"/{settings.do_bucket}/"
            if bucket_part in product.image_url:
                file_name = product.image_url.split(bucket_part)[-1]
                await storage_service.delete_file(file_name)
        except Exception as e:
            print(f"Error deleting file: {e}")

    await product_service.delete_product(product_id)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(call.id, "Product removed successfully.")

    msg = (
        f"Product removed successfully!\n\n"
        f"Product ID: {product_id}\n"
        f"Product Name: {product.name}\n"
    )
    await bot.send_message(call.message.chat.id, msg)
    await show_products_to_remove(call.message.chat.id, 0)


@bot.callback_query_handler(func=lambda call: call.data.startswith(VIEW_FEEDBACKS_CQ_PREFIX))
@admin_guard
async def handle_view_feedbacks(call):
    page_str = call.data.removeprefix(VIEW_FEEDBACKS_CQ_PREFIX)
    page = int(page_str) if page_str.isdigit() else 0
    limit = 5
    offset = page * limit
    
    feedback_service = FeedbackService()
    total_count = await feedback_service.get_feedbacks_count()
    feedbacks = await feedback_service.get_feedbacks_list(limit, offset)
    
    total_pages = (total_count + limit - 1) // limit
    if total_pages == 0:
        total_pages = 1
    
    if not feedbacks and page > 0:
        await bot.answer_callback_query(call.id, "No more feedbacks.")
        return

    msg = f"Feedbacks (Page {page + 1}/{total_pages}):"
    
    # If it's a new message (e.g. from main menu), we send a new message.
    # But here we are handling callback query, so we edit.
    # Wait, the button in admin menu sends a callback query too.
    
    try:
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=msg,
            reply_markup=feedbacks_list_keyboard(feedbacks, page, total_pages)
        )
    except Exception as e:
        # If content is same, it might raise error, but here we are changing content likely.
        # Or if we are coming from a different message type.
        # Let's just try to send if edit fails? No, edit should work.
        print(f"Error editing message: {e}")
        await bot.send_message(
            call.message.chat.id,
            msg,
            reply_markup=feedbacks_list_keyboard(feedbacks, page, total_pages)
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith(VIEW_FEEDBACK_DETAILS_CQ_PREFIX))
@admin_guard
async def handle_feedback_details(call):
    feedback_id = int(call.data.removeprefix(VIEW_FEEDBACK_DETAILS_CQ_PREFIX))
    feedback_service = FeedbackService()
    feedback = await feedback_service.get_feedback_by_id(feedback_id)
    
    if not feedback:
        await bot.answer_callback_query(call.id, "Feedback not found.")
        return
        
    username = f"@{feedback.user_telegram_username}" if feedback.user_telegram_username else f"ID: {feedback.user_id}"
    msg = (
        f"Feedback Details:\n\n"
        f"From: {username}\n"
        f"Date: {feedback.created_at}\n\n"
        f"{feedback.feedback}"
    )
    
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=msg,
        reply_markup=feedback_details_keyboard(0)
    )

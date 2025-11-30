from telebot.types import Message

from ..constants import (
    BROWSE_CATALOG_MESSAGE,
    BUY_PRODUCT_CQ_PREFIX,
    CATALOG_CMD,
    NEXT_CATALOG_CQ_PREFIX,
    PRODUCT_DETAILS_CQ_PREFIX,
)
from ..keyboards.inline import buy_product_keyboard, catalog_keyboard, payment_keyboard
from ..loader import bot
from ..services.orders import OrdersService
from ..services.payments import PaymentService
from ..services.products import GetProductsListParams, ProductService
from ..services.users import UsersService


async def send_catalog(message: Message, user_cursor: int = 0):
    products_service = ProductService()
    params: GetProductsListParams = GetProductsListParams(
        limit=6, cursor=user_cursor, sort_desc=True
    )
    products, next_cursor = await products_service.get_products_list(params)
    total_count = await products_service.get_products_count()

    msg = None
    if user_cursor == 0:
        msg = """Here is our product catalog. Browse through our selection of amazing products!\n
Total products available: {total_count}.\n
Good luck! 🎉
""".format(total_count=total_count)
    else:
        msg = "Here are more products from our catalog! Enjoy browsing! 🎉"

    await bot.send_message(
        message.chat.id, msg, reply_markup=catalog_keyboard(products, next_cursor)
    )


@bot.message_handler(commands=[CATALOG_CMD])
async def cmd_catalog(message: Message):
    await send_catalog(message)


@bot.message_handler(func=lambda message: message.text == BROWSE_CATALOG_MESSAGE)
async def handle_browse_catalog(message: Message):
    await send_catalog(message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(NEXT_CATALOG_CQ_PREFIX)
)
async def handle_catalog_pagination(call):
    cursor_str = call.data.removeprefix(NEXT_CATALOG_CQ_PREFIX)
    cursor = int(cursor_str) if cursor_str.isdigit() else 0
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await send_catalog(call.message, cursor)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(PRODUCT_DETAILS_CQ_PREFIX)
)
async def handle_product_details(call):
    product_id_str = call.data.removeprefix(PRODUCT_DETAILS_CQ_PREFIX)
    if not product_id_str.isdigit():
        bot.answer_callback_query(call.id, "Invalid product ID.")
        return

    product_id = int(product_id_str)
    products_service = ProductService()
    product = await products_service.get_product_by_id(product_id)

    if product is None:
        bot.answer_callback_query(call.id, "Product not found.")
        return

    msg = f"""Product Details:\n
Name: {product.name}
Description: {product.description or "No description available."}
Price: {product.price} {product.currency}
"""

    await bot.send_photo(
        call.message.chat.id,
        product.image_url,
        caption=msg,
        reply_markup=buy_product_keyboard(product.id),
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(BUY_PRODUCT_CQ_PREFIX)
)
async def handle_buy_product(call):
    product_id_str = call.data.removeprefix(BUY_PRODUCT_CQ_PREFIX)
    if not product_id_str.isdigit():
        bot.answer_callback_query(call.id, "Invalid product ID.")
        return

    product_id = int(product_id_str)

    orders_service = OrdersService()
    users_service = UsersService()

    username = call.from_user.username
    if username is None:
        await bot.answer_callback_query(
            call.id, "Only users without username can place orders."
        )
        return

    user = await users_service.get_or_create_user(
        call.from_user.id, call.from_user.username
    )

    # Get product details for payment
    products_service = ProductService()
    product = await products_service.get_product_by_id(product_id)
    if not product:
        await bot.answer_callback_query(call.id, "Product not found.")
        return

    order = await orders_service.create_order(product_id, user.id)

    # Create Stripe Checkout Session
    payment_service = PaymentService()
    try:
        session_id, payment_url = await payment_service.create_checkout_session(
            order.id, product.name, product.price, product.currency
        )
        await orders_service.update_order_payment_info(order.id, session_id, payment_url)

        msg = f"""Order Created Successfully! 🎉\n
Order ID: {order.id}
Status: {order.status}
Price: {product.price} {product.currency}

Please complete the payment using the button below. 👇
"""
        await bot.send_message(
            call.message.chat.id, msg, reply_markup=payment_keyboard(payment_url, order.id)
        )

    except Exception as e:
        await bot.send_message(call.message.chat.id, f"Error creating payment: {e}")
        # Optionally cancel order or log error

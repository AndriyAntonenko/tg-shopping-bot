from telebot.types import Message
from ..loader import bot
from ..keyboards.inline import catalog_keyboard, buy_product_keyboard
from ..services.products import ProductService, GetProductsListParams
from ..services.orders import OrdersService
from ..services.users import UsersService

from ..constants import CATALOG_CMD, NEXT_CATALOG_CQ_PREFIX, PRODUCT_DETAILS_CQ_PREFIX, BUY_PRODUCT_CQ_PREFIX, BROWSE_CATALOG_MESSAGE


async def send_catalog(message: Message, user_cursor: int = 0):
    products_service = ProductService()
    params: GetProductsListParams = GetProductsListParams(limit=6, cursor=user_cursor, sort_desc=True)
    products, next_cursor = await products_service.get_products_list(params)
    total_count = await products_service.get_products_count()

    msg = None
    if user_cursor == 0:
      msg = '''Here is our product catalog. Browse through our selection of amazing products!\n
Total products available: {total_count}.\n
Good luck! 🎉
'''.format(total_count=total_count)
    else:
      msg = 'Here are more products from our catalog! Enjoy browsing! 🎉'    

    
    await bot.send_message(message.chat.id, msg, reply_markup=catalog_keyboard(products, next_cursor))


@bot.message_handler(commands=[CATALOG_CMD])
async def cmd_catalog(message: Message):
    await send_catalog(message)


@bot.message_handler(func=lambda message: message.text == BROWSE_CATALOG_MESSAGE)
async def handle_browse_catalog(message: Message):
    await send_catalog(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith(NEXT_CATALOG_CQ_PREFIX))
async def handle_catalog_pagination(call):
    cursor_str = call.data.removeprefix(NEXT_CATALOG_CQ_PREFIX)
    cursor = int(cursor_str) if cursor_str.isdigit() else 0
    await send_catalog(call.message, cursor)


@bot.callback_query_handler(func=lambda call: call.data.startswith(PRODUCT_DETAILS_CQ_PREFIX))
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
  
    msg = f'''Product Details:\n
Name: {product.name}
Description: {product.description or "No description available."}
Price: {product.price} {product.currency}
'''
    
    await bot.send_photo(call.message.chat.id, product.image_url, caption=msg, reply_markup=buy_product_keyboard(product.id))


@bot.callback_query_handler(func=lambda call: call.data.startswith(BUY_PRODUCT_CQ_PREFIX))
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
        await bot.answer_callback_query(call.id, f"Only users without username can place orders.")
        return
    
    user = await users_service.get_or_create_user(
        call.from_user.id,
        call.from_user.username
    )

    order = await orders_service.create_order(product_id, user.id)

    msg = f'''Order Created Successfully! 🎉\n
Order ID: {order.id}
Status: {order.status}
Thank you for your purchase! 🛒

Our administrator will contact you soon to finalize the details.
'''
    
    await bot.send_message(call.message.chat.id, msg)

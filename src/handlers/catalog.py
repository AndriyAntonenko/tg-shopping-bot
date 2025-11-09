from telebot.types import Message
from ..loader import bot
from ..keyboards.inline import catalog_keyboard, buy_product_keyboard
from ..db.connection import get_db_connection
from ..services.products import ProductService, GetProductsListParams


def send_catalog(message: Message, user_cursor: int = 0):
    products_service = ProductService(get_db_connection())
    params: GetProductsListParams = GetProductsListParams(limit=6, cursor=user_cursor, sort_desc=True)
    products, next_cursor = products_service.get_products_list(params)
    total_count = products_service.get_products_count()

    msg = None
    if user_cursor == 0:
      msg = '''Here is our product catalog. Browse through our selection of amazing products!\n
Total products available: {total_count}.\n
Good luck! 🎉
'''.format(total_count=total_count)
    else:
      msg = 'Here are more products from our catalog! Enjoy browsing! 🎉'    

    
    bot.send_message(message.chat.id, msg, reply_markup=catalog_keyboard(products, next_cursor))


@bot.message_handler(commands=["catalog"])
def cmd_catalog(message: Message):
    send_catalog(message)


@bot.message_handler(func=lambda message: message.text == "Browse catalog")
def handle_browse_catalog(message: Message):
    send_catalog(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("catalog_cursor_"))
def handle_catalog_pagination(call):
    cursor_str = call.data.removeprefix("catalog_cursor_")
    cursor = int(cursor_str) if cursor_str.isdigit() else 0
    send_catalog(call.message, cursor)


@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def handle_product_details(call):
    product_id_str = call.data.removeprefix("product_")
    if not product_id_str.isdigit():
        bot.answer_callback_query(call.id, "Invalid product ID.")
        return

    product_id = int(product_id_str)
    products_service = ProductService(get_db_connection())
    product = products_service.get_product_by_id(product_id)

    if product is None:
        bot.answer_callback_query(call.id, "Product not found.")
        return
  
    msg = f'''Product Details:\n
Name: {product.name}
Description: {product.description or "No description available."}
Price: {product.price} {product.currency}
'''
    
    print(product)
    bot.send_photo(call.message.chat.id, product.image_url, caption=msg, reply_markup=buy_product_keyboard(product.id))
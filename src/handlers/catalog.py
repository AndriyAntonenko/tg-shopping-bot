from telebot.types import Message
from ..loader import bot
from ..keyboards.inline import catalog_keyboard
from ..db.connection import get_db_connection
from ..services.products import ProductService, GetProductsListParams

def send_catalog(message: Message, cursor: int = 0):
    products_service = ProductService(get_db_connection())
    params: GetProductsListParams = GetProductsListParams(limit=6, cursor=cursor, sort_desc=True)
    products, cursor = products_service.get_products_list(params)
    bot.send_message(message.chat.id, "Here is the product catalog", reply_markup=catalog_keyboard(products, cursor))


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

from telebot.types import Message
from telebot import util

from ..constants import HELP_CMD, HELP_MESSAGE, START_CMD
from ..keyboards.reply import main_menu
from ..loader import bot
from .common import check_payment_logic


async def send_help_message(message: Message):
    help_message = """Here are some commands to get you started:\n
/start - Start interaction with the bot.
/help - Get assistance and see what I can do.
/info - Learn more about this bot.
/catalog - Browse out product catalog."""
    await bot.send_message(message.chat.id, help_message, reply_markup=main_menu())


HELLO_MESSAGE = """Hey there! 👋\n
I'm your friendly online-shop bot. Here are some commands to get you started

/help - Get assistance and see what I can do.
/info - Learn more about this bot.
/catalog - Browse out product catalog."""

def extract_deeplink_order_id(payload: str):
    # check if payload starts with "order_"
    if not payload.startswith("order_"):
        return None
    
    # extract order id
    order_id = payload.removeprefix("order_")
    if not order_id.isdigit():
        return None
    return int(order_id)


@bot.message_handler(commands=[START_CMD])
async def cmd_start(message: Message):
    payload = util.extract_arguments(message.text)
    order_id = extract_deeplink_order_id(payload)
    if order_id:
        try:
            await bot.delete_message(message.chat.id, message.message_id)
            await check_payment_logic(message.chat.id, message.from_user.id, order_id, None)
        except:
            pass
    else:
        await bot.send_message(message.chat.id, HELLO_MESSAGE, reply_markup=main_menu())



@bot.message_handler(commands=[HELP_CMD])
async def cmd_help(message: Message):
    await send_help_message(message)


@bot.message_handler(func=lambda message: message.text == HELP_MESSAGE)
async def handle_help(message: Message):
    await send_help_message(message)

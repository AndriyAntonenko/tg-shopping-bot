from telebot import util
from telebot.types import Message

from ..constants import HELP_CMD, START_CMD
from ..keyboards.reply import main_menu
from ..loader import bot
from ..resources.strings import get_string
from .common import check_payment_logic


async def send_help_message(message: Message):
    lang_code = getattr(message, "language_code", "en")
    help_message = get_string("help_message", lang_code)
    await bot.send_message(
        message.chat.id, help_message, reply_markup=main_menu(lang_code)
    )


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
            lang_code = getattr(message, "language_code", "en")
            await bot.delete_message(message.chat.id, message.message_id)
            await check_payment_logic(
                message.chat.id,
                message.from_user.id,
                order_id,
                None,
                lang_code=lang_code,
            )
        except:
            pass
    else:
        lang_code = getattr(message, "language_code", "en")
        await bot.send_message(
            message.chat.id,
            get_string("hello_message", lang_code),
            reply_markup=main_menu(lang_code),
        )


@bot.message_handler(commands=[HELP_CMD])
async def cmd_help(message: Message):
    await send_help_message(message)


@bot.message_handler(
    func=lambda message: message.text
    in [get_string("help", "en"), get_string("help", "uk")]
)
async def handle_help(message: Message):
    await send_help_message(message)

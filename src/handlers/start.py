from telebot.types import Message
from ..loader import bot
from ..keyboards.reply import main_menu

from ..constants import HELP_CMD, START_CMD, HELP_MESSAGE


async def send_help_message(message: Message):
  help_message = '''Here are some commands to get you started:\n
/start - Start interaction with the bot.
/help - Get assistance and see what I can do.
/info - Learn more about this bot.
/catalog - Browse out product catalog.'''
  await bot.send_message(message.chat.id, help_message, reply_markup=main_menu())


HELLO_MESSAGE = '''Hey there! 👋\n
I'm your friendly online-shop bot. Here are some commands to get you started

/help - Get assistance and see what I can do.
/info - Learn more about this bot.
/catalog - Browse out product catalog.'''

@bot.message_handler(commands=[START_CMD])
async def cmd_start(message: Message):
  await bot.send_message(message.chat.id, HELLO_MESSAGE, reply_markup=main_menu())


@bot.message_handler(commands=[HELP_CMD])
async def cmd_help(message: Message):
  await send_help_message(message)


@bot.message_handler(func=lambda message: message.text == HELP_MESSAGE)
async def handle_help(message: Message):
  await send_help_message(message)

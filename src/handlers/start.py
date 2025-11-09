from telebot.types import Message
from ..loader import bot
from ..keyboards.reply import main_menu

HELLO_MESSAGE = '''Hey there! 👋\n
I'm your friendly online-shop bot. Here are some commands to get you started

/help - Get assistance and see what I can do.
/info - Learn more about this bot.
/catalog - Browse out product catalog.'''

@bot.message_handler(commands=["start"])
def cmd_start(message: Message):
  bot.send_message(message.chat.id, HELLO_MESSAGE, reply_markup=main_menu())

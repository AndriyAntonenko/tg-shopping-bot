from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from ..constants import BROWSE_CATALOG_MESSAGE, HELP_MESSAGE

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(BROWSE_CATALOG_MESSAGE), KeyboardButton(HELP_MESSAGE))
    return kb

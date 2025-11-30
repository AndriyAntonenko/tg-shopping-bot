from telebot.types import KeyboardButton, ReplyKeyboardMarkup

from ..constants import BROWSE_CATALOG_MESSAGE, FEEDBACK_MESSAGE, HELP_MESSAGE


def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(BROWSE_CATALOG_MESSAGE), KeyboardButton(FEEDBACK_MESSAGE))
    kb.add(KeyboardButton(HELP_MESSAGE))
    return kb

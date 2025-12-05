from telebot.types import KeyboardButton, ReplyKeyboardMarkup

from ..resources.strings import get_string


def main_menu(lang_code: str = "en"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton(get_string("browse_catalog", lang_code)),
        KeyboardButton(get_string("feedback", lang_code)),
    )
    kb.add(KeyboardButton(get_string("help", lang_code)))
    kb.add(KeyboardButton(get_string("language_btn", lang_code)))
    return kb

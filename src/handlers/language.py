from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from ..constants import LANGUAGE_CMD
from ..keyboards.reply import main_menu
from ..loader import bot
from ..resources.strings import get_string
from ..services.users import UsersService

users_service = UsersService()


@bot.message_handler(commands=[LANGUAGE_CMD])
async def cmd_language(message: Message):
    lang_code = getattr(message, "language_code", "en")

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en"),
        InlineKeyboardButton("Українська 🇺🇦", callback_data="set_lang_uk"),
    )

    await bot.send_message(
        message.chat.id,
        get_string("choose_language", lang_code),
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_"))
async def handle_language_selection(call: CallbackQuery):
    lang_code = call.data.split("_")[-1]

    await users_service.update_user_language(call.from_user.id, lang_code)

    # Update language code on the call object so get_string uses the new language immediately
    call.language_code = lang_code

    await bot.answer_callback_query(call.id)
    await bot.send_message(
        call.message.chat.id,
        get_string("language_changed", lang_code),
        reply_markup=main_menu(lang_code),
    )


@bot.message_handler(
    func=lambda message: message.text
    in [get_string("language_btn", "en"), get_string("language_btn", "uk")]
)
async def handle_language_btn(message: Message):
    await cmd_language(message)

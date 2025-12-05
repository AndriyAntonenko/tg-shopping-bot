import uuid
from typing import Annotated

from pydantic import Field, TypeAdapter, ValidationError
from telebot.asyncio_handler_backends import State, StatesGroup

from src.constants import ADD_PRODUCT_CMD, DEFAULT_CURRENCY
from src.guards.admin import admin_guard
from src.loader import bot
from src.resources.strings import get_string
from src.services.products import ProductService
from src.services.storage import StorageService

name_validator = TypeAdapter(Annotated[str, Field(min_length=2, max_length=32)])
description_validator = TypeAdapter(
    Annotated[str, Field(min_length=10, max_length=256)]
)
price_validator = TypeAdapter(Annotated[float, Field(gt=0)])


class AddProductState(StatesGroup):
    name = State()
    description = State()
    price = State()
    image_url = State()


@bot.message_handler(commands=[ADD_PRODUCT_CMD])
@admin_guard
async def cmd_add_product(message):
    await bot.set_state(message.from_user.id, AddProductState.name, message.chat.id)
    lang_code = getattr(message, "language_code", "en")
    await bot.send_message(message.chat.id, get_string("enter_product_name", lang_code))


@bot.message_handler(state=AddProductState.name)
async def handle_product_name(message):
    name_raw = message.text.strip()
    lang_code = getattr(message, "language_code", "en")
    try:
        name = name_validator.validate_python(name_raw)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["name"] = name

        await bot.set_state(
            message.from_user.id, AddProductState.description, message.chat.id
        )
        msg = get_string("enter_product_description", lang_code).format(name=name)
        await bot.send_message(message.chat.id, msg)
    except ValidationError:
        await bot.send_message(
            message.chat.id,
            get_string("invalid_product_name", lang_code),
        )
        return


@bot.message_handler(state=AddProductState.description)
async def handle_product_description(message):
    description_raw = message.text.strip()
    lang_code = getattr(message, "language_code", "en")
    try:
        description = description_validator.validate_python(description_raw)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["description"] = description
        await bot.set_state(
            message.from_user.id, AddProductState.price, message.chat.id
        )
        await bot.send_message(
            message.chat.id,
            get_string("enter_product_price", lang_code),
        )
    except ValidationError:
        await bot.send_message(
            message.chat.id,
            get_string("invalid_product_description", lang_code),
        )
        return


@bot.message_handler(state=AddProductState.price)
async def handle_product_price(message):
    price_raw = message.text.strip()
    lang_code = getattr(message, "language_code", "en")
    try:
        price = price_validator.validate_python(price_raw)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["price"] = price
        await bot.set_state(
            message.from_user.id, AddProductState.image_url, message.chat.id
        )
        await bot.send_message(
            message.chat.id, get_string("enter_product_image", lang_code)
        )
    except ValidationError:
        await bot.send_message(
            message.chat.id,
            get_string("invalid_product_price", lang_code),
        )
        return


@bot.message_handler(state=AddProductState.image_url, content_types=["photo"])
async def handle_product_image(message):
    lang_code = getattr(message, "language_code", "en")
    if not message.photo:
        await bot.send_message(
            message.chat.id, get_string("invalid_product_image", lang_code)
        )
        return

    try:
        photo_file_id = message.photo[-1].file_id
        photo_file = await bot.get_file(photo_file_id)
        image_data = await bot.download_file(photo_file.file_path)

        storage = StorageService()
        product_service = ProductService()
        file_ext = photo_file.file_path.split(".")[-1]
        file_name = f"products/{uuid.uuid4()}.{file_ext}"

        image_url = await storage.upload_file(
            image_data, file_name, "image/jpeg"
        )  # Telegram photos are usually JPEGs

        if not image_url:
            await bot.send_message(
                message.chat.id, get_string("error_upload_image", lang_code)
            )
            return

        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["image_url"] = image_url

            await product_service.add_product(
                name=data["name"],
                description=data["description"],
                image_url=data["image_url"],
                price=data["price"],
                currency=DEFAULT_CURRENCY,
            )

            caption = get_string("product_added", lang_code).format(
                name=data["name"],
                description=data["description"],
                price=data["price"],
            )
            await bot.delete_state(message.from_user.id, message.chat.id)
            await bot.send_photo(message.chat.id, image_url, caption=caption)
    except Exception as e:
        print(f"Error in handle_product_image: {e}")
        await bot.send_message(
            message.chat.id, get_string("error_processing_image", lang_code)
        )

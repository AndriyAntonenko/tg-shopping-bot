import uuid
from telebot.asyncio_handler_backends import State, StatesGroup
from src.loader import bot
from src.constants import ADD_PRODUCT_CMD
from src.guards.admin import admin_guard
from src.services.storage import StorageService
from src.services.products import ProductService
from src.constants import DEFAULT_CURRENCY

from typing import Annotated
from pydantic import TypeAdapter, Field, ValidationError

name_validator = TypeAdapter(Annotated[str, Field(min_length=2, max_length=32)])
description_validator = TypeAdapter(Annotated[str, Field(min_length=10, max_length=256)])
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
  await bot.send_message(message.chat.id, "Please enter the product name:")

@bot.message_handler(state=AddProductState.name)
async def handle_product_name(message):
  name_raw = message.text.strip()
  try:
    name = name_validator.validate_python(name_raw)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
      data['name'] = name

    await bot.set_state(message.from_user.id, AddProductState.description, message.chat.id)
    msg = "Great! Now, please enter the product description for {}:".format(name)
    await bot.send_message(message.chat.id, msg)
  except ValidationError as e:
    await bot.send_message(message.chat.id, "Invalid product name. Please enter a name between 2 and 32 characters:")
    return

@bot.message_handler(state=AddProductState.description)
async def handle_product_description(message):
  description_raw = message.text.strip()
  try:
    description = description_validator.validate_python(description_raw)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
      data['description'] = description
    await bot.set_state(message.from_user.id, AddProductState.price, message.chat.id)
    await bot.send_message(message.chat.id, "Great! Now, please enter the product price (a positive number):")
  except ValidationError as e:
    await bot.send_message(message.chat.id, "Invalid description. Please enter a description between 10 and 256 characters:")
    return

@bot.message_handler(state=AddProductState.price)
async def handle_product_price(message):
  price_raw = message.text.strip()
  try:
    price = price_validator.validate_python(price_raw)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
      data['price'] = price
    await bot.set_state(message.from_user.id, AddProductState.image_url, message.chat.id)
    await bot.send_message(message.chat.id, "Almost done! Now, please add the product image:")
  except ValidationError as e:
    await bot.send_message(message.chat.id, "Invalid price. Please enter a positive number for the price:")
    return

@bot.message_handler(state=AddProductState.image_url, content_types=['photo'])
async def handle_product_image(message):
  if not message.photo:
    await bot.send_message(message.chat.id, "Please send a valid photo for the product image:")
    return
  
  try:
    photo_file_id = message.photo[-1].file_id
    photo_file = await bot.get_file(photo_file_id)
    image_data = await bot.download_file(photo_file.file_path)
    
    storage = StorageService()
    product_service = ProductService()
    file_ext = photo_file.file_path.split('.')[-1]
    file_name = f"products/{uuid.uuid4()}.{file_ext}"
    
    image_url = await storage.upload_file(image_data, file_name, 'image/jpeg') # Telegram photos are usually JPEGs
    
    if not image_url:
       await bot.send_message(message.chat.id, "Failed to upload image. Please try again.")
       return

    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
      data['image_url'] = image_url

      await product_service.add_product(
        name=data['name'],
        description=data['description'],
        image_url=data['image_url'],
        price=data['price'],
        currency=DEFAULT_CURRENCY
      )

      caption = f'''Product successfully added:\n
Name: {data['name']}
Description: {data['description']}
Price: {data['price']}
'''
      await bot.delete_state(message.from_user.id, message.chat.id)
      await bot.send_photo(
        message.chat.id,
        image_url,
        caption=caption
      )
  except Exception as e:
    print(f"Error in handle_product_image: {e}")
    await bot.send_message(message.chat.id, "An error occurred while processing the image.")

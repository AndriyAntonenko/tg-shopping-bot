from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from ..services.products import ProductItem

def catalog_keyboard(products: list[ProductItem], cursor_id: int | None = None) -> InlineKeyboardMarkup:
  kb = InlineKeyboardMarkup(row_width=2)
  kb.add(
    *[InlineKeyboardButton(text=f"{product.name} - {product.price} {product.currency}", callback_data=f"product_{product.id}") for product in products]
  )
  if cursor_id is not None:
    kb.add(InlineKeyboardButton(text="Next ▶️", callback_data=f"catalog_cursor_{cursor_id}"))
  return kb

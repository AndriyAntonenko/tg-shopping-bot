from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..constants import (
    APPROVE_ORDER_CQ_PREFIX,
    BUY_PRODUCT_CQ_PREFIX,
    CANCEL_ORDER_CQ_PREFIX,
    NEXT_CATALOG_CQ_PREFIX,
    PRODUCT_DETAILS_CQ_PREFIX,
    VIEW_ORDER_DETAILS_CQ_PREFIX,
    VIEW_PENDING_ORDERS_CQ,
)
from ..services.orders import OrderItemDetailed
from ..services.products import ProductItem


def catalog_keyboard(
    products: list[ProductItem], cursor_id: int | None = None
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        *[
            InlineKeyboardButton(
                text=f"{product.name} - {product.price} {product.currency}",
                callback_data=f"{PRODUCT_DETAILS_CQ_PREFIX}{product.id}",
            )
            for product in products
        ]
    )
    if cursor_id is not None:
        kb.add(
            InlineKeyboardButton(
                text="Next ▶️", callback_data=f"{NEXT_CATALOG_CQ_PREFIX}{cursor_id}"
            )
        )
    return kb


def buy_product_keyboard(product_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            text="Buy 🛒", callback_data=f"{BUY_PRODUCT_CQ_PREFIX}{product_id}"
        )
    )
    return kb


def admin_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            text="View Pending Orders", callback_data=VIEW_PENDING_ORDERS_CQ
        )
    )
    return kb


def pending_orders_keyboard(orders: list[OrderItemDetailed]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for order in orders:
        kb.add(
            InlineKeyboardButton(
                text=f"#{order.id}: @{order.user_telegram_username} ordered {order.product_name}",
                callback_data=f"{VIEW_ORDER_DETAILS_CQ_PREFIX}{order.id}",
            )
        )
    return kb


def admin_order_commands_keyboard(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(
            text="Approve ✅", callback_data=f"{APPROVE_ORDER_CQ_PREFIX}{order_id}"
        ),
        InlineKeyboardButton(
            text="Cancel ❌", callback_data=f"{CANCEL_ORDER_CQ_PREFIX}{order_id}"
        ),
    )
    return kb

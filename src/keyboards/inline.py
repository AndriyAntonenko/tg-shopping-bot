from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..constants import (
    APPROVE_ORDER_CQ_PREFIX,
    BUY_PRODUCT_CQ_PREFIX,
    CANCEL_ORDER_CQ_PREFIX,
    CHECK_PAYMENT_CQ_PREFIX,
    NEXT_CATALOG_CQ_PREFIX,
    PRODUCT_DETAILS_CQ_PREFIX,
    VIEW_ORDER_DETAILS_CQ_PREFIX,
    VIEW_PENDING_ORDERS_CQ,

    REMOVE_PRODUCT_PREFIX,
    CONFIRM_REMOVE_PRODUCT_PREFIX,
    CANCEL_REMOVE_PRODUCT_PREFIX,
    REMOVE_PRODUCT_CURSOR_PREFIX,
    VIEW_FEEDBACKS_CQ_PREFIX,
    VIEW_FEEDBACK_DETAILS_CQ_PREFIX,
)
from ..services.feedback import Feedback
from ..services.orders import OrderItemDetailed, OrderStatus
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
    kb.add(
        InlineKeyboardButton(
            text="Feedbacks", callback_data=f"{VIEW_FEEDBACKS_CQ_PREFIX}0"
        )
    )
    return kb


def pending_orders_keyboard(orders: list[OrderItemDetailed]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for order in orders:
        paid_data = "PAID ✅" if order.status == OrderStatus.PAID else "UNPAID ❌"
        kb.add(
            InlineKeyboardButton(
                text=f"No.{order.id}: {order.user_telegram_username} ordered {order.product_name}. {paid_data}",
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

def admin_remove_products_keyboard(products: list[ProductItem], next_cursor: int | None = None) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        *[
            InlineKeyboardButton(
                text=f"{product.name} ({product.price} {product.currency})",
                callback_data=f"{REMOVE_PRODUCT_PREFIX}{product.id}",
            )
            for product in products
        ]
    )

    if next_cursor:
        markup.add(
            InlineKeyboardButton(
                text="Next Page >>", callback_data=f"{REMOVE_PRODUCT_CURSOR_PREFIX}{next_cursor}"
            )
        )
    return markup


def confirm_remove_product_keyboard(product_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="Yes, Remove", callback_data=f"{CONFIRM_REMOVE_PRODUCT_PREFIX}{product_id}"
        ),
        InlineKeyboardButton(
            text="No, Cancel", callback_data=f"{CANCEL_REMOVE_PRODUCT_PREFIX}"
        ),
    )
    return markup


def payment_keyboard(payment_url: str, order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(text="Pay Now 💳", url=payment_url)
    )
    kb.add(
        InlineKeyboardButton(
            text="I have paid ✅", callback_data=f"{CHECK_PAYMENT_CQ_PREFIX}{order_id}"
        )
    )
    return kb
    return kb


def feedbacks_list_keyboard(
    feedbacks: list[Feedback], page: int, total_pages: int
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for feedback in feedbacks:
        username = f"@{feedback.user_telegram_username}" if feedback.user_telegram_username else f"ID: {feedback.user_id}"
        text = f"{username}: {feedback.feedback[:30]}..."
        kb.add(
            InlineKeyboardButton(
                text=text,
                callback_data=f"{VIEW_FEEDBACK_DETAILS_CQ_PREFIX}{feedback.id}",
            )
        )

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Prev", callback_data=f"{VIEW_FEEDBACKS_CQ_PREFIX}{page - 1}"
            )
        )
    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Next ➡️", callback_data=f"{VIEW_FEEDBACKS_CQ_PREFIX}{page + 1}"
            )
        )
    if nav_buttons:
        kb.row(*nav_buttons)

    return kb


def feedback_details_keyboard(back_page: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            text="Back to List", callback_data=f"{VIEW_FEEDBACKS_CQ_PREFIX}{back_page}"
        )
    )
    return kb

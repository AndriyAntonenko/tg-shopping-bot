from dataclasses import dataclass
from enum import Enum

from ..db.connection import get_db_connection


class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELED = "canceled"


@dataclass
class OrderItem:
    id: int
    product_id: int
    user_id: int
    status: str
    created_at: str
    stripe_session_id: str | None = None
    payment_url: str | None = None


@dataclass
class OrderItemDetailed:
    id: int
    product_id: int
    user_id: int
    status: OrderStatus
    created_at: str
    product_name: str
    product_price: float
    product_currency: str
    user_telegram_user_id: int
    user_telegram_username: str


def from_db_row_to_order_item(row) -> OrderItem:
    # row: id, product_id, user_id, status, created_at, stripe_session_id, payment_url
    # Ensure row has enough elements, handle cases where new columns might be missing if query not updated
    stripe_session_id = row[5] if len(row) > 5 else None
    payment_url = row[6] if len(row) > 6 else None
    return OrderItem(
        id=row[0],
        product_id=row[1],
        user_id=row[2],
        status=row[3],
        created_at=row[4],
        stripe_session_id=stripe_session_id,
        payment_url=payment_url,
    )


def from_db_row_to_order_item_detailed(row) -> OrderItemDetailed:
    return OrderItemDetailed(
        id=row[0],
        product_id=row[1],
        user_id=row[2],
        status=OrderStatus(row[3]),
        created_at=row[4],
        product_name=row[5],
        product_price=row[6],
        product_currency=row[7],
        user_telegram_user_id=row[8],
        user_telegram_username=row[9],
    )


class OrdersService:
    async def create_order(self, product_id: int, user_id: int) -> OrderItem:
        conn = await get_db_connection()
        cursor = await conn.cursor()

        await cursor.execute(
            """
      INSERT INTO orders (product_id, user_id, status)
      VALUES (?, ?, ?)
      RETURNING id, product_id, user_id, status, created_at;
      """,
            (product_id, user_id, OrderStatus.PENDING.value),
        )

        new_order = await cursor.fetchone()
        await conn.commit()

        return from_db_row_to_order_item(new_order)

    async def get_pending_orders_list(
        self, ids: list[int] | None
    ) -> list[OrderItemDetailed]:
        conn = await get_db_connection()
        cursor = await conn.cursor()

        ids_condition = (
            " AND o.id IN ({})".format(",".join("?" * len(ids))) if ids else ""
        )

        query = """
        SELECT
            o.id AS id,
            o.product_id AS product_id,
            o.user_id AS user_id,
            o.status AS status,
            o.created_at AS created_at,
            p.name AS product_name,
            p.price AS product_price,
            p.currency AS product_currency,
            u.telegram_user_id AS user_telegram_user_id,
            u.telegram_username AS user_telegram_username
        FROM orders o
        INNER JOIN users u ON o.user_id = u.id
        INNER JOIN products p ON o.product_id = p.id
        WHERE status IN (?, ?) {ids_condition}
        ORDER BY o.created_at ASC;
        """.format(ids_condition=ids_condition)
        await cursor.execute(
            query, (OrderStatus.PENDING.value, OrderStatus.PAID.value, *(ids or []))
        )

        rows = await cursor.fetchall()

        return [from_db_row_to_order_item_detailed(row) for row in rows]

    async def get_pending_orders_count(self) -> int:
        conn = await get_db_connection()
        cursor = await conn.cursor()

        await cursor.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE status IN (?, ?);
            """,
            (OrderStatus.PENDING.value, OrderStatus.PAID.value),
        )

        count = (await cursor.fetchone())[0]
        return int(count)

    async def update_order_status(self, order_id: int, new_status: OrderStatus) -> bool:
        conn = await get_db_connection()
        cursor = await conn.cursor()

        await cursor.execute(
            """
      UPDATE orders
      SET status = ?
      WHERE id = ?;
      """,
            (
                new_status.value,
                order_id,
            ),
        )

        updated_rows = cursor.rowcount
        await conn.commit()

        return updated_rows > 0

    async def update_order_payment_info(
        self, order_id: int, stripe_session_id: str, payment_url: str
    ) -> bool:
        conn = await get_db_connection()
        cursor = await conn.cursor()

        await cursor.execute(
            """
      UPDATE orders
      SET stripe_session_id = ?, payment_url = ?
      WHERE id = ?;
      """,
            (
                stripe_session_id,
                payment_url,
                order_id,
            ),
        )

        updated_rows = cursor.rowcount
        await conn.commit()

        return updated_rows > 0

    async def get_order_by_id(self, order_id: int) -> OrderItem | None:
        conn = await get_db_connection()
        cursor = await conn.cursor()

        await cursor.execute(
            """
            SELECT 
                id,
                product_id,
                user_id,
                status,
                created_at,
                stripe_session_id,
                payment_url
            FROM orders
            WHERE id = ?;
            """,
            (order_id,),
        )

        row = await cursor.fetchone()
        if row:
            return from_db_row_to_order_item(row)
        return None

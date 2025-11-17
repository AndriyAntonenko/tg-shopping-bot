from ..db.connection import get_db_connection
from enum import Enum
from dataclasses import dataclass


class OrderStatus(Enum):
  PENDING = "pending"
  COMPLETED = "completed"
  CANCELED = "canceled"


@dataclass
class OrderItem:
  id: int
  product_id: int
  user_id: int
  status: str
  created_at: str


def from_db_row_to_order_item(row) -> OrderItem:
  return OrderItem(
    id=row[0],
    product_id=row[1],
    user_id=row[2],
    status=row[3],
    created_at=row[4]
  )


class OrdersService:
  def create_order(self, product_id: int, user_id: int) -> OrderItem:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
      '''
      INSERT INTO orders (product_id, user_id, status)
      VALUES (?, ?, ?)
      RETURNING id, product_id, user_id, status, created_at;
      ''',
      (product_id, user_id, OrderStatus.PENDING.value)
    )

    new_order = cursor.fetchone()
    conn.commit()

    return from_db_row_to_order_item(new_order)
    
from ..db.connection import get_db_connection
from dataclasses import dataclass

@dataclass
class User:
  id: int
  telegram_user_id: int
  telegram_username: str
  created_at: str
  is_admin: bool

def from_db_row_to_user(row) -> User:
  return User(
    id=row[0],
    telegram_user_id=row[1],
    telegram_username=row[2],
    created_at=row[3],
    is_admin=bool(row[4])
  )

class UsersService:
  def get_or_create_user(
    self,
    telegram_user_id,
    telegram_username: str
  ) -> User:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
      '''
      INSERT INTO users (telegram_user_id, telegram_username)
      VALUES (?, ?)
      ON CONFLICT(telegram_user_id) DO UPDATE SET telegram_username=excluded.telegram_username
      RETURNING id, telegram_user_id, telegram_username, created_at, is_admin;
      ''',
      (telegram_user_id, telegram_username)
    )

    user_row = cursor.fetchone()
    conn.commit()

    return from_db_row_to_user(user_row)


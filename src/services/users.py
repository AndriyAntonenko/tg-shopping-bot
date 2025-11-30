from dataclasses import dataclass

from ..db.connection import get_db_connection


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
        is_admin=bool(row[4]),
    )


class UsersService:
    async def get_user_if_exists(self, telegram_user_id) -> User | None:
        conn = await get_db_connection()
        cursor = await conn.cursor()

        await cursor.execute(
            """
      SELECT id, telegram_user_id, telegram_username, created_at, is_admin
      FROM users
      WHERE telegram_user_id = ?;
      """,
            (telegram_user_id,),
        )

        user_row = await cursor.fetchone()
        if user_row is None:
            return None

        return from_db_row_to_user(user_row)

    async def get_or_create_user(
        self, telegram_user_id, telegram_username: str
    ) -> User:
        conn = await get_db_connection()
        cursor = await conn.cursor()

        await cursor.execute(
            """
      INSERT INTO users (telegram_user_id, telegram_username)
      VALUES (?, ?)
      ON CONFLICT(telegram_user_id) DO UPDATE SET telegram_username=excluded.telegram_username
      RETURNING id, telegram_user_id, telegram_username, created_at, is_admin;
      """,
            (telegram_user_id, telegram_username),
        )

        user_row = await cursor.fetchone()
        await conn.commit()

        return from_db_row_to_user(user_row)

    async def get_admins(self) -> list[User]:
        conn = await get_db_connection()
        cursor = await conn.cursor()

        await cursor.execute(
            """
            SELECT id, telegram_user_id, telegram_username, created_at, is_admin
            FROM users
            WHERE is_admin = 1;
            """
        )

        rows = await cursor.fetchall()
        return [from_db_row_to_user(row) for row in rows]

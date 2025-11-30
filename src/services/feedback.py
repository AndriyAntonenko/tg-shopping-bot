from dataclasses import dataclass
from ..db.connection import get_db_connection


@dataclass
class Feedback:
    id: int
    user_id: int
    feedback: str
    created_at: str
    user_telegram_username: str | None = None


class FeedbackService:
    async def create_feedback(self, user_id: int, feedback_text: str):
        conn = await get_db_connection()
        cursor = await conn.cursor()

        await cursor.execute(
            """
            INSERT INTO user_feedbacks (user_id, feedback)
            VALUES (?, ?)
            """,
            (user_id, feedback_text),
        )

        await conn.commit()

    async def get_feedbacks_count(self) -> int:
        conn = await get_db_connection()
        cursor = await conn.cursor()
        await cursor.execute("SELECT COUNT(*) FROM user_feedbacks")
        count = await cursor.fetchone()
        return count[0] if count else 0

    async def get_feedbacks_list(self, limit: int, offset: int) -> list[Feedback]:
        conn = await get_db_connection()
        cursor = await conn.cursor()

        await cursor.execute(
            """
            SELECT f.id, f.user_id, f.feedback, f.created_at, u.telegram_username
            FROM user_feedbacks f
            LEFT JOIN users u ON f.user_id = u.id
            ORDER BY f.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )

        rows = await cursor.fetchall()
        return [
            Feedback(
                id=row[0],
                user_id=row[1],
                feedback=row[2],
                created_at=row[3],
                user_telegram_username=row[4],
            )
            for row in rows
        ]

    async def get_feedback_by_id(self, feedback_id: int) -> Feedback | None:
        conn = await get_db_connection()
        cursor = await conn.cursor()

        await cursor.execute(
            """
            SELECT f.id, f.user_id, f.feedback, f.created_at, u.telegram_username
            FROM user_feedbacks f
            LEFT JOIN users u ON f.user_id = u.id
            WHERE f.id = ?
            """,
            (feedback_id,),
        )

        row = await cursor.fetchone()
        if not row:
            return None

        return Feedback(
            id=row[0],
            user_id=row[1],
            feedback=row[2],
            created_at=row[3],
            user_telegram_username=row[4],
        )

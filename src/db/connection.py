import aiosqlite

from ..config import settings


async def get_db_connection():
    connection = await aiosqlite.connect(settings.database_path)
    return connection

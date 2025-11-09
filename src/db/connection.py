import sqlite3
from ..config import settings

def get_db_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.database_path)
    return connection

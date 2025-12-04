import logging
import os

from aiosqlite import Connection

from .connection import get_db_connection

logger = logging.getLogger(__name__)


async def apply_migrations():
    db_connection: Connection = await get_db_connection()
    cursor = await db_connection.cursor()

    # Create migrations table
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            filename TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Get list of migration files
    migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
    migration_files = sorted(
        [f for f in os.listdir(migrations_dir) if f.endswith(".sql")]
    )

    for filename in migration_files:
        # Check if migration already applied
        await cursor.execute("SELECT 1 FROM migrations WHERE filename = ?", (filename,))
        if await cursor.fetchone():
            logger.info("Migration already applied: %s", filename)
            continue

        logger.info(f"Applying migration: {filename}")

        # Read and execute migration
        file_path = os.path.join(migrations_dir, filename)
        with open(file_path, "r") as f:
            sql_script = f.read()
            await cursor.executescript(sql_script)

        # Record migration
        await cursor.execute(
            "INSERT INTO migrations (filename) VALUES (?)", (filename,)
        )
        await db_connection.commit()

    await db_connection.commit()
    logger.info("Database migrations completed.")

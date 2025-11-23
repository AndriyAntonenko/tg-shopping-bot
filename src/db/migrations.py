import logging

from aiosqlite import Connection

from ..config import settings
from .connection import get_db_connection


async def apply_migrations():
    db_connection: Connection = await get_db_connection()
    cursor = await db_connection.cursor()

    await cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT,
      image_url TEXT,
      price REAL NOT NULL,
      currency TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  """)

    await cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_id INTEGER NOT NULL,
      user_id INTEGER NOT NULL,
      status TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (product_id) REFERENCES products(id),
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  """)

    await cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      telegram_user_id INTEGER NOT NULL UNIQUE,
      telegram_username TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      is_admin BOOLEAN DEFAULT FALSE
    )
    """
    )

    if settings.administrator_id and settings.administrator_username:
        await cursor.execute(
            """
      INSERT INTO users(telegram_user_id, telegram_username, is_admin)
      VALUES (?, ?, TRUE)
      ON CONFLICT DO UPDATE SET is_admin=TRUE;
      """,
            (settings.administrator_id, settings.administrator_username),
        )

    if settings.initial_products_json:
        try:
            with open(settings.initial_products_json, "r", encoding="utf-8") as f:
                import json

                products = json.load(f)
                for product in products:
                    await cursor.execute(
                        """
              INSERT INTO products (name, description, image_url, price, currency)
              VALUES (?, ?, ?, ?, ?)
              """,
                        (
                            product.get("name"),
                            product.get("description"),
                            product.get("image_url"),
                            product.get("price"),
                            product.get("currency"),
                        ),
                    )
        except FileNotFoundError:
            logging.getLogger(__name__).warning(
                f"Initial products JSON file not found at {settings.initial_products_json}. Skipping initial data load."
            )

    await db_connection.commit()

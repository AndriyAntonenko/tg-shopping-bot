from sqlite3 import Connection
from ..config import settings
from .connection import get_db_connection
import logging

def apply_migrations():
  db_connection: Connection = get_db_connection()
  cursor = db_connection.cursor()

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT,
      image_url TEXT,
      price REAL NOT NULL,
      currency TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  ''')

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_id INTEGER NOT NULL,
      user_id INTEGER NOT NULL,
      status TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (product_id) REFERENCES products(id)
    )
  ''')

  if settings.initial_products_json:
    try:
      with open(settings.initial_products_json, "r", encoding="utf-8") as f:
        import json
        products = json.load(f)
        for product in products:
          cursor.execute(
              '''
              INSERT INTO products (name, description, image_url, price, currency)
              VALUES (?, ?, ?, ?, ?)
              ''',
              (
                  product.get("name"),
                  product.get("description"),
                  product.get("image_url"),
                  product.get("price"),
                  product.get("currency")
              )
          )
    except FileNotFoundError:
      logging.getLogger(__name__).warning(f"Initial products JSON file not found at {settings.initial_products_json}. Skipping initial data load.")

  db_connection.commit()
  
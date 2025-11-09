from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class Settings:
  bot_token: str = os.getenv("TG_BOT_KEY", "")
  parse_mode: str = "HTML"
  skip_pending: bool = True
  long_polling_timeout: int = 20
  database_path: str = os.getenv("DATABASE_PATH", "")
  initial_products_json: str = os.getenv("INITIAL_PRODUCTS_JSON", None)

settings = Settings()

if not settings.bot_token:
  raise RuntimeError("TG_BOT_KEY is not set in environment variables.")

if not settings.database_path:
  raise RuntimeError("DATABASE_PATH is not set in environment variables.")

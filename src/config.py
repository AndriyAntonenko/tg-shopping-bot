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
  administrator_id: int = int(os.getenv("ADMINISTRATOR_ID", "0"))
  administrator_username: str = os.getenv("ADMINISTRATOR_USERNAME", "")
  initial_products_json: str = os.getenv("INITIAL_PRODUCTS_JSON", None)

  do_region: str = os.getenv("DO_SPACES_REGION", "")
  do_endpoint: str = os.getenv("DO_SPACES_ENDPOINT", "")
  do_key: str = os.getenv("DO_SPACES_KEY", "")
  do_secret: str = os.getenv("DO_SPACES_SECRET", "")
  do_bucket: str = os.getenv("DO_SPACES_BUCKET", "")

settings = Settings()

if not settings.bot_token:
  raise RuntimeError("TG_BOT_KEY is not set in environment variables.")

if not settings.database_path:
  raise RuntimeError("DATABASE_PATH is not set in environment variables.")

if settings.administrator_id == 0:
  raise RuntimeError("ADMINISTRATOR_ID is not set in environment variables.")

if settings.administrator_username == "":
  raise RuntimeError("ADMINISTRATOR_USERNAME is not set in environment variables.")

# validating DigitalOcean settings
if not settings.do_region:
  raise RuntimeError("DO_SPACES_REGION is not set in environment variables.")

if not settings.do_endpoint:
  raise RuntimeError("DO_SPACES_ENDPOINT is not set in environment variables.")

if not settings.do_key:
  raise RuntimeError("DO_SPACES_KEY is not set in environment variables.")

if not settings.do_secret:
  raise RuntimeError("DO_SPACES_SECRET is not set in environment variables.")

if not settings.do_bucket:
  raise RuntimeError("DO_SPACES_BUCKET is not set in environment variables.")

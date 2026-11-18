import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
MAX_PAGES = int(os.getenv("MAX_PAGES", "12"))

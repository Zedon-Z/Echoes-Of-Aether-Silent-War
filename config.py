import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", 1378500453))
APP_URL = os.getenv("APP_URL")

import os
from dotenv import load_dotenv
from telegram.ext import Updater
load_dotenv()

updater = Updater(token=os.getenv("TOKEN"), use_context=True)


BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", 1378500453))
APP_URL = os.getenv("APP_URL")

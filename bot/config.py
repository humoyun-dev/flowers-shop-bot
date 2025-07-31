import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN_SELLER = os.getenv("BOT_TOKEN_SELLER")
BOT_TOKEN_CUSTOMER = os.getenv("BOT_TOKEN_CUSTOMER")
DATABASE_URL = os.getenv("DATABASE_URL")

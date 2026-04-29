import os

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# tokens por canal (luego irán a DB por tenant)
FACEBOOK_TOKEN = os.getenv("VERIFY_TOKEN")
INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
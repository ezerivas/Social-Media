import os
from dotenv import load_dotenv

load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mi_token_secreto")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "")
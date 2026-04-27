import os

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
DATABASE_URL = os.getenv("${{ Postgres.DATABASE_URL }}")
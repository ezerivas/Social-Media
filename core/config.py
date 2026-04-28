import os


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
    PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")


settings = Settings()
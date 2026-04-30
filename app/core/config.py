import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # El nombre a la izquierda es como lo usas en Python
    # El nombre en os.getenv es como debe llamarse en el Dashboard de Railway
    FB_VERIFY_TOKEN: str = os.getenv("FACEBOOK_VERIFY_TOKEN", "FACEBOOK_TOKEN")
    DATABASE_URL: str = os.getenv("DATABASE_URL")

settings = Settings()
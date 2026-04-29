import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # El nombre a la izquierda es como lo usas en Python
    # El nombre en os.getenv es como debe llamarse en el Dashboard de Railway
    FB_VERIFY_TOKEN: str = os.getenv("VERIFY_TOKEN", "tu_token_por_defecto")
    DATABASE_URL: str = os.getenv("DATABASE_URL")

settings = Settings()
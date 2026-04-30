from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FACEBOOK_VERIFY_TOKEN: str = "FACEBOOK_TOKEN"
    DATABASE_URL: str

settings = Settings()
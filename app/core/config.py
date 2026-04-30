from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    FACEBOOK_VERIFY_TOKEN: str = "FACEBOOK_TOKEN"
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
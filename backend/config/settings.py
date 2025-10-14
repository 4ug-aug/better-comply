from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    SECRET_KEY: str =os.getenv("SECRET_KEY", "change-me-in-env")
    ACCESS_TOKEN_EXPIRATION_DAYS: int = 30
    REFRESH_TOKEN_EXPIRATION_DAYS: int = 30
    ALGORITHM: str = "HS256"
    FRONTEND_URL: str = "http://localhost"


settings = Settings()
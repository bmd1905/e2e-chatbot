import os

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(find_dotenv(raise_error_if_not_found=True))


class Settings(BaseSettings):
    # ------------------ Database ------------------
    database_url: str = os.environ.get("DATABASE_URL")
    secret_key: str = os.environ.get("SECRET_KEY", "secret")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # ------------------ Redis ------------------
    redis_url: str = os.environ.get("REDIS_URL", "redis://localhost")
    use_redis: bool = True

    class ConfigDict:
        env_file = ".env"


settings = Settings()

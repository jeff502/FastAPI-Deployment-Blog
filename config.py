from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    # Tells Pydantic to read from .env file

    secret_key: SecretStr  # Won't leak in logs or prints
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    max_upload_size_bytes: int = 5 * 1024 * 1024 # 5mb


settings = Settings()  # type: ignore[call-arg]  # Loaded from .env file

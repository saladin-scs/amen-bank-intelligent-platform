from pydantic_settings import BaseSettings

from amenbank_shared.config import BaseServiceSettings


class Settings(BaseServiceSettings):
    service_name: str = "auth-service"
    database_url: str = "postgresql+asyncpg://amenbank:changeme@localhost:5432/amenbank"
    redis_url: str = "redis://localhost:6379/0"
    jwt_refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"


settings = Settings()

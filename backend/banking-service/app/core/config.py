from pydantic_settings import BaseSettings

from amenbank_shared.config import BaseServiceSettings


class Settings(BaseServiceSettings):
    service_name: str = "banking-service"
    database_url: str = "postgresql+asyncpg://amenbank:changeme@localhost:5432/amenbank"


settings = Settings()

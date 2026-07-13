from pydantic_settings import BaseSettings


class BaseServiceSettings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:4200,http://localhost:80"

    jwt_secret_key: str = "change-this-to-a-long-random-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"

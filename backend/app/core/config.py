from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "My Events API"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()

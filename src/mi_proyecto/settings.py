from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Orders API"
    environment: str = "development"
    secret_key: str = "clave_local_desarrollo"
    database_url: str = "sqlite:///./orders_api.db"
    allowed_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()

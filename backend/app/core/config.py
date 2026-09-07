from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_name: str = "DocuMind AI"
    project_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"

    # SQLite database
    database_url: str = "sqlite:///./documind.db"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()
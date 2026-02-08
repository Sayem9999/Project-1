from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "edit.ai API"
    api_prefix: str = "/api"
    secret_key: str
    jwt_algorithm: str = "HS256"
    token_expiry_minutes: int = 60 * 24
    database_url: str = "sqlite+aiosqlite:///./storage/edit_ai.db"
    storage_root: str = "storage"
    frontend_url: str = "http://localhost:3000"
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    groq_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

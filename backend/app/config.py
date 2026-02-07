from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "edit.ai API"
    api_prefix: str = "/api"
    secret_key: str
    jwt_algorithm: str = "HS256"
    token_expiry_minutes: int = 60 * 24
    database_url: str = "sqlite+aiosqlite:///./storage/edit_ai.db"
    storage_root: str = "storage"
    n8n_webhook_url: str = "http://n8n:5678/webhook/edit-ai-process"
    frontend_url: str = "http://localhost:3000"
    frontend_origins: str | None = None
    openai_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        raw = self.frontend_origins or self.frontend_url
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


settings = Settings()

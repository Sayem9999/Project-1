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
    environment: str = "development"
    rate_limit_enabled: bool = True
    sentry_dsn: str | None = None
    
    # AI API Keys
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    
    # OAuth - Google
    google_client_id: str | None = None
    google_client_secret: str | None = None
    
    # OAuth - GitHub
    github_client_id: str | None = None
    github_client_secret: str | None = None
    
    # Cloudflare R2 Storage
    r2_account_id: str | None = None
    r2_access_key_id: str | None = None
    r2_secret_access_key: str | None = None
    r2_bucket_name: str = "proedit-storage"
    r2_public_url: str | None = None  # e.g., https://pub-xxx.r2.dev

    # Stripe (Optional)
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_id_pro: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

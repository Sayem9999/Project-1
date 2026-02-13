import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Prioritize local .env over system-level environment variables to avoid 
# shadow-conflicts (e.g. DATABASE_URL from Render vs local SQLite).
load_dotenv(override=True)

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
    credits_enabled: bool = True
    monthly_credits_default: int = 10
    sentry_dsn: str | None = None
    redis_url: str | None = None
    celery_video_queue: str = "video"
    
    # AI API Keys
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    llm_primary_provider: str = "gemini"
    llm_fallback_provider: str = "groq"
    
    # Ollama (Local LLM)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:1b"
    ollama_enabled: bool = True
    password_policy: str = "basic"
    
    # OAuth - Google
    google_client_id: str | None = None
    google_client_secret: str | None = None
    
    # OAuth - GitHub
    github_client_id: str | None = None
    github_client_secret: str | None = None

    # Admin Bootstrap
    # Primary bootstrap admin account for first-party operations.
    admin_bootstrap_email: str | None = "sayemf21@gmail.com"
    admin_bootstrap_once: bool = True
    
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

    # Modal (GPU Offloading)
    modal_token_id: str | None = None
    modal_token_secret: str | None = None

    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{os.getenv('ENVIRONMENT', 'development')}"),
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    def validate_required_settings(self):
        """Validate that essential settings are present in non-development environments."""
        if self.environment != "development":
            missing = [field for field in ["secret_key"] if not getattr(self, field)]
            if missing:
                raise ValueError(f"Missing required settings for {self.environment}: {', '.join(missing)}")

            if not (self.gemini_api_key or self.groq_api_key or self.openai_api_key):
                raise ValueError(
                    f"Missing required settings for {self.environment}: at least one LLM API key"
                )

            if self.redis_url and not (self.redis_url.startswith("redis://") or self.redis_url.startswith("rediss://")):
                raise ValueError("Invalid REDIS_URL: must start with redis:// or rediss://")


settings = Settings()

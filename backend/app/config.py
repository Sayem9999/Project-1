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
    openai_models_csv: str = "gpt-4o-mini,gpt-4o"
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    openrouter_api_key: str | None = None
    llm_primary_provider: str = "gemini"
    llm_fallback_provider: str = "groq"
    llm_request_timeout_seconds: float = 90.0
    llm_total_timeout_seconds: float = 180.0
    
    # Ollama (Local LLM)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_enabled: bool = True
    openrouter_enabled: bool = True
    password_policy: str = "basic"
    
    # OAuth - Google
    google_client_id: str | None = None
    google_client_secret: str | None = None
    
    # OAuth - GitHub
    github_client_id: str | None = None
    github_client_secret: str | None = None

    # Admin Bootstrap
    # Keep unset by default; enable explicitly through environment.
    admin_bootstrap_email: str | None = None
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

    # n8n Outbound Webhooks
    n8n_base_url: str | None = None
    n8n_webhook_secret: str | None = None
    n8n_job_status_path: str = "/webhook/proedit/job-status"
    n8n_timeout_seconds: float = 3.0
    n8n_retry_attempts: int = 2
    n8n_retry_backoff_seconds: float = 0.25

    # Inbound Orchestration Callback Security
    orchestration_webhook_secret: str | None = None
    orchestration_webhook_tolerance_seconds: int = 300

    # Modal (GPU Offloading)
    modal_token_id: str | None = None
    modal_token_secret: str | None = None

    # Idle Autonomy (Self-Heal + Self-Improve)
    autonomy_enabled: bool = True
    autonomy_profile_mode: str = "conservative"
    autonomy_poll_seconds: int = 30
    autonomy_idle_heal_interval_seconds: int = 300
    autonomy_idle_improve_interval_seconds: int = 1800
    autonomy_stuck_job_minutes: int = 180

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

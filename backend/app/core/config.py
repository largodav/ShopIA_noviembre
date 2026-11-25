from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_version: str = "v003-a"
    cors_origins: str = "http://localhost:5173,https://largodav.github.io"

    backend_host_os: str = "Windows"
    backend_host_name: str = "win-home-1"

    auth_enabled: bool = True
    auth_username: str = "david"
    auth_password: str = "shopia2026"
    auth_secret: str = "shopia-local-dev-secret-change-me"
    auth_token_ttl_days: int = 90

    database_url: str = "postgresql+psycopg://shopia:shopia@db:5432/shopia"

    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_fast_model: str = "gemma4-e2b-uncensored:latest"
    ollama_advisor_model: str = "gemma4-e2b-uncensored:latest"
    ollama_embed_model: str = "nomic-embed-text"
    ollama_timeout_seconds: float = 120.0

    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_subject: str = "mailto:admin@shopia.local"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()

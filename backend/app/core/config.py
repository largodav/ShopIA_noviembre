from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_version: str = "v001-b"
    cors_origins: str = "http://localhost:5173,https://localhost:5173"

    database_url: str = "postgresql+psycopg://shopia:shopia@db:5432/shopia"

    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_fast_model: str = "gemma4-e2b-uncensored:latest"
    ollama_advisor_model: str = "gemma4-e2b-uncensored:latest"
    ollama_embed_model: str = "nomic-embed-text"
    ollama_timeout_seconds: float = 20.0

    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_subject: str = "mailto:admin@shopia.local"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "MedIntel AI CRM"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://medintel:medintel_password@localhost:5432/medintel"
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    frontend_url: str = "http://localhost:5173"
    rate_limit: str = "120/minute"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

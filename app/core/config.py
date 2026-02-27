from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "TSSie"
    VERSION: str = "2.1.0"
    
    SUPABASE_URL: str
    SUPABASE_KEY: str # Idealmente será a Service Role Key para bypassing RLS onde necessário
    
    REDIS_URL: str = "redis://localhost:6379"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

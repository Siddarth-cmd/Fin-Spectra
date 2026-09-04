from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    groq_api_key: str = "gsk_placeholder"
    groq_model: str = "llama-3.3-70b-versatile"
    mock_llm_mode: bool = False
    
    database_url: str = "sqlite:///./nova.db"
    
    port: int = 8000
    env: str = "development"
    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

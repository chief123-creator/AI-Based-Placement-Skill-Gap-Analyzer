from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: str = "your-secret-key-change-in-prod"
    PROJECT_NAME: str = "AI Placement Analyzer"
    
    class Config:
        env_file = ".env"

settings = Settings()

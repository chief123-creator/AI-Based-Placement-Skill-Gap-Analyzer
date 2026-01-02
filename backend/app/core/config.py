from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "your-secret-key-change-in-prod"
    PROJECT_NAME: str = "AI Placement Analyzer"
    
    class Config:
        env_file = ".env"

settings = Settings()

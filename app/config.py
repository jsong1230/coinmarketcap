from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # CoinMarketCap API
    cmc_api_key: str = os.getenv("CMC_API_KEY", "test_key")
    
    # Telegram Bot
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "test_token")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./cryptowatcher.db")
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Scheduler
    scheduler_interval_minutes: int = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "5"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


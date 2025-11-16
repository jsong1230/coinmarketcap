from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # CoinMarketCap API
    cmc_api_key: str
    
    # Telegram Bot
    telegram_bot_token: str
    
    # Database
    database_url: str = "sqlite:///./cryptowatcher.db"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Scheduler
    scheduler_interval_minutes: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


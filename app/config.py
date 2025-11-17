from pydantic_settings import BaseSettings
from typing import Optional
import os
import json


class Settings(BaseSettings):
    # CoinMarketCap API
    cmc_api_key: str = os.getenv("CMC_API_KEY", "test_key")
    
    # Telegram Bot
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "test_token")
    telegram_chat_id: Optional[str] = os.getenv("TELEGRAM_CHAT_ID", None)
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./cryptowatcher.db")
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Scheduler
    scheduler_interval_minutes: int = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "5"))
    
    # Portfolio (JSON string)
    portfolio_json: Optional[str] = os.getenv("PORTFOLIO_JSON", None)
    
    # Base currency
    base_currency: str = os.getenv("BASE_CURRENCY", "KRW")
    
    @property
    def portfolio(self) -> Optional[dict]:
        """포트폴리오를 딕셔너리로 반환"""
        if not self.portfolio_json:
            return None
        try:
            return json.loads(self.portfolio_json)
        except json.JSONDecodeError:
            return None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


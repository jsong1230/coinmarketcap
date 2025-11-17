from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class UserCreate(BaseModel):
    telegram_chat_id: str
    cmc_api_key: Optional[str] = None
    cmc_portfolio_id: Optional[str] = None
    base_currency: str = "KRW"


class UserUpdate(BaseModel):
    cmc_api_key: Optional[str] = None
    cmc_portfolio_id: Optional[str] = None
    base_currency: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    telegram_chat_id: str
    cmc_portfolio_id: Optional[str]
    base_currency: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class PortfolioItemCreate(BaseModel):
    symbol: str
    quantity: float


class PortfolioItemResponse(BaseModel):
    id: int
    symbol: str
    quantity: float
    
    class Config:
        from_attributes = True


class AlertSettingsCreate(BaseModel):
    single_coin_percentage_threshold: Optional[float] = 5.0
    single_coin_absolute_threshold: Optional[float] = None
    portfolio_percentage_threshold: Optional[float] = 10.0
    portfolio_absolute_threshold: Optional[float] = None
    min_notification_interval_minutes: int = 15


class AlertSettingsResponse(BaseModel):
    id: int
    single_coin_percentage_threshold: float
    single_coin_absolute_threshold: Optional[float]
    portfolio_percentage_threshold: float
    portfolio_absolute_threshold: Optional[float]
    min_notification_interval_minutes: int
    
    class Config:
        from_attributes = True


class PriceSnapshotResponse(BaseModel):
    id: int
    snapshot_data: Dict[str, Any]
    total_portfolio_value: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class PortfolioSummaryResponse(BaseModel):
    total_value: float
    base_currency: str
    items: list[PortfolioItemResponse]
    price_data: Dict[str, Any]


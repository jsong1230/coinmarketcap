from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_chat_id = Column(String, unique=True, index=True, nullable=False)
    cmc_api_key = Column(String, nullable=True)
    cmc_portfolio_id = Column(String, nullable=True)
    base_currency = Column(String, default="KRW")  # USD or KRW
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    portfolio_items = relationship("PortfolioItem", back_populates="user", cascade="all, delete-orphan")
    alert_settings = relationship("AlertSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    price_snapshots = relationship("PriceSnapshot", back_populates="user", cascade="all, delete-orphan")


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False)  # BTC, ETH, etc.
    quantity = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="portfolio_items")


class AlertSettings(Base):
    __tablename__ = "alert_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Single coin thresholds
    single_coin_percentage_threshold = Column(Float, default=5.0)  # %
    single_coin_absolute_threshold = Column(Float, nullable=True)  # absolute price change
    
    # Portfolio thresholds
    portfolio_percentage_threshold = Column(Float, default=10.0)  # %
    portfolio_absolute_threshold = Column(Float, nullable=True)  # absolute value change
    
    # Notification settings
    min_notification_interval_minutes = Column(Integer, default=15)  # 최소 알림 간격 (분)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="alert_settings")


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    snapshot_data = Column(JSON, nullable=False)  # {symbol: {price, value, ...}}
    total_portfolio_value = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="price_snapshots")


from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import logging
import threading

from app.database import get_db, engine, Base
from app.models import User, PortfolioItem, AlertSettings
from app.schemas import (
    UserCreate, UserResponse,
    PortfolioItemCreate, PortfolioItemResponse,
    AlertSettingsCreate, AlertSettingsResponse,
    PortfolioSummaryResponse
)
from app.services import PortfolioService, AlertService
from app.telegram_bot import TelegramBot
from app.scheduler import MonitoringScheduler
from app.config import settings

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 전역 변수
telegram_bot = None
scheduler = None
bot_thread = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행"""
    global telegram_bot, scheduler, bot_thread
    
    # 데이터베이스 테이블 생성
    Base.metadata.create_all(bind=engine)
    logger.info("데이터베이스 테이블 생성 완료")
    
    # 텔레그램 봇 초기화 (별도 스레드에서 실행)
    try:
        telegram_bot = TelegramBot()
        scheduler = MonitoringScheduler(telegram_bot)
        scheduler.start()
        logger.info("스케줄러 시작 완료")
        
        # 텔레그램 봇을 별도 스레드에서 실행
        def run_bot():
            try:
                telegram_bot.run()
            except Exception as e:
                logger.error(f"텔레그램 봇 실행 오류: {e}")
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("텔레그램 봇 시작 완료")
    except Exception as e:
        logger.error(f"텔레그램 봇/스케줄러 초기화 실패: {e}")
    
    yield
    
    # 종료 시 정리
    if scheduler:
        scheduler.scheduler.shutdown()
    if telegram_bot:
        telegram_bot.application.stop()
    logger.info("애플리케이션 종료")


app = FastAPI(
    title="CryptoWatcher Bot API",
    description="CoinMarketCap 포트폴리오 모니터링 및 텔레그램 알림 서비스",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "CryptoWatcher Bot API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# 사용자 관련 API
@app.post("/api/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """사용자 등록"""
    existing_user = db.query(User).filter(
        User.telegram_chat_id == user_data.telegram_chat_id
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 등록된 사용자입니다.")
    
    new_user = User(
        telegram_chat_id=user_data.telegram_chat_id,
        cmc_api_key=user_data.cmc_api_key,
        cmc_portfolio_id=user_data.cmc_portfolio_id,
        base_currency=user_data.base_currency
    )
    db.add(new_user)
    
    # 기본 알림 설정 생성
    alert_settings = AlertSettings(user_id=new_user.id)
    db.add(alert_settings)
    
    db.commit()
    db.refresh(new_user)
    
    return new_user


@app.get("/api/users/{telegram_chat_id}", response_model=UserResponse)
async def get_user(telegram_chat_id: str, db: Session = Depends(get_db)):
    """사용자 조회"""
    user = db.query(User).filter(User.telegram_chat_id == telegram_chat_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user


# 포트폴리오 관련 API
@app.post("/api/portfolio", response_model=PortfolioItemResponse)
async def add_portfolio_item(
    item_data: PortfolioItemCreate,
    telegram_chat_id: str,
    db: Session = Depends(get_db)
):
    """포트폴리오 항목 추가"""
    user = db.query(User).filter(User.telegram_chat_id == telegram_chat_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    service = PortfolioService(db)
    portfolio_item = service.add_portfolio_item(
        user.id,
        item_data.symbol,
        item_data.quantity
    )
    
    return portfolio_item


@app.get("/api/portfolio/summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary(
    telegram_chat_id: str,
    db: Session = Depends(get_db)
):
    """포트폴리오 요약 조회"""
    user = db.query(User).filter(User.telegram_chat_id == telegram_chat_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    service = PortfolioService(db)
    summary = service.get_portfolio_summary(user.id)
    
    if not summary:
        raise HTTPException(status_code=404, detail="포트폴리오가 설정되지 않았습니다.")
    
    return summary


# 알림 설정 관련 API
@app.get("/api/alerts", response_model=AlertSettingsResponse)
async def get_alert_settings(
    telegram_chat_id: str,
    db: Session = Depends(get_db)
):
    """알림 설정 조회"""
    user = db.query(User).filter(User.telegram_chat_id == telegram_chat_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    alert_settings = db.query(AlertSettings).filter(
        AlertSettings.user_id == user.id
    ).first()
    
    if not alert_settings:
        raise HTTPException(status_code=404, detail="알림 설정이 없습니다.")
    
    return alert_settings


@app.put("/api/alerts", response_model=AlertSettingsResponse)
async def update_alert_settings(
    alert_data: AlertSettingsCreate,
    telegram_chat_id: str,
    db: Session = Depends(get_db)
):
    """알림 설정 업데이트"""
    user = db.query(User).filter(User.telegram_chat_id == telegram_chat_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    alert_settings = db.query(AlertSettings).filter(
        AlertSettings.user_id == user.id
    ).first()
    
    if not alert_settings:
        # 새로 생성
        alert_settings = AlertSettings(user_id=user.id)
        db.add(alert_settings)
    
    # 설정 업데이트
    if alert_data.single_coin_percentage_threshold is not None:
        alert_settings.single_coin_percentage_threshold = alert_data.single_coin_percentage_threshold
    if alert_data.single_coin_absolute_threshold is not None:
        alert_settings.single_coin_absolute_threshold = alert_data.single_coin_absolute_threshold
    if alert_data.portfolio_percentage_threshold is not None:
        alert_settings.portfolio_percentage_threshold = alert_data.portfolio_percentage_threshold
    if alert_data.portfolio_absolute_threshold is not None:
        alert_settings.portfolio_absolute_threshold = alert_data.portfolio_absolute_threshold
    if alert_data.min_notification_interval_minutes is not None:
        alert_settings.min_notification_interval_minutes = alert_data.min_notification_interval_minutes
    
    db.commit()
    db.refresh(alert_settings)
    
    return alert_settings


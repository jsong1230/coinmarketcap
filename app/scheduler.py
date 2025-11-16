from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.services import PortfolioService, AlertService
from app.telegram_bot import TelegramBot
from app.config import settings
import logging
from telegram import Bot

logger = logging.getLogger(__name__)


class MonitoringScheduler:
    """포트폴리오 모니터링 스케줄러"""
    
    def __init__(self, telegram_bot: TelegramBot):
        self.scheduler = AsyncIOScheduler()
        self.telegram_bot = telegram_bot
        self.bot = Bot(token=settings.telegram_bot_token)
    
    async def check_portfolio_and_alert(self):
        """포트폴리오 확인 및 알림 전송"""
        db = SessionLocal()
        
        try:
            users = db.query(User).all()
            
            for user in users:
                try:
                    portfolio_service = PortfolioService(db)
                    summary = portfolio_service.get_portfolio_summary(user.id)
                    
                    if not summary:
                        continue
                    
                    # 스냅샷 저장
                    alert_service = AlertService(db)
                    price_data = {
                        symbol: {
                            "price": data.get("price", 0),
                            "market_cap": data.get("market_cap", 0),
                            "percent_change_24h": data.get("percent_change_24h", 0)
                        }
                        for symbol, data in summary["price_data"].items()
                    }
                    alert_service.save_snapshot(
                        user.id,
                        price_data,
                        summary["total_value"]
                    )
                    
                    # 알림 확인
                    alerts = alert_service.check_alerts(user.id)
                    
                    for alert in alerts:
                        try:
                            await self.bot.send_message(
                                chat_id=user.telegram_chat_id,
                                text=alert["message"]
                            )
                            logger.info(f"알림 전송 완료: user_id={user.id}, type={alert['type']}")
                        except Exception as e:
                            logger.error(f"알림 전송 실패: user_id={user.id}, error={e}")
                
                except Exception as e:
                    logger.error(f"사용자 {user.id} 포트폴리오 확인 실패: {e}")
        
        except Exception as e:
            logger.error(f"스케줄러 실행 오류: {e}")
        finally:
            db.close()
    
    async def send_hourly_summary(self):
        """1시간마다 포트폴리오 요약 전송"""
        db = SessionLocal()
        
        try:
            users = db.query(User).all()
            
            for user in users:
                try:
                    portfolio_service = PortfolioService(db)
                    summary = portfolio_service.get_portfolio_summary(user.id)
                    
                    if not summary:
                        continue
                    
                    # 포트폴리오 요약 메시지 생성
                    message = f"📊 포트폴리오 요약 ({user.base_currency})\n\n"
                    message += f"총 평가액: {summary['total_value']:,.0f} {user.base_currency}\n\n"
                    
                    for item in summary['items']:
                        symbol = item['symbol']
                        quantity = item['quantity']
                        price_info = summary['price_data'].get(symbol, {})
                        price = price_info.get('price', 0)
                        value = quantity * price
                        change_24h = price_info.get('percent_change_24h', 0)
                        
                        message += f"💰 {symbol}\n"
                        message += f"   수량: {quantity:,.6f}\n"
                        message += f"   현재가: {price:,.2f} {user.base_currency}\n"
                        message += f"   평가액: {value:,.2f} {user.base_currency}\n"
                        message += f"   24h 변동: {change_24h:+.2f}%\n\n"
                    
                    try:
                        await self.bot.send_message(
                            chat_id=user.telegram_chat_id,
                            text=message
                        )
                        logger.info(f"1시간 요약 전송 완료: user_id={user.id}")
                    except Exception as e:
                        logger.error(f"1시간 요약 전송 실패: user_id={user.id}, error={e}")
                
                except Exception as e:
                    logger.error(f"사용자 {user.id} 요약 생성 실패: {e}")
        
        except Exception as e:
            logger.error(f"1시간 요약 스케줄러 실행 오류: {e}")
        finally:
            db.close()
    
    def start(self):
        """스케줄러 시작"""
        # 포트폴리오 모니터링 (5분마다)
        interval_minutes = settings.scheduler_interval_minutes
        self.scheduler.add_job(
            self.check_portfolio_and_alert,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id="portfolio_monitor",
            replace_existing=True
        )
        logger.info(f"포트폴리오 모니터링 스케줄러 시작: {interval_minutes}분 간격")
        
        # 1시간마다 요약 전송
        self.scheduler.add_job(
            self.send_hourly_summary,
            trigger=IntervalTrigger(hours=1),
            id="hourly_summary",
            replace_existing=True
        )
        logger.info("1시간 요약 스케줄러 시작: 1시간 간격")
        
        self.scheduler.start()


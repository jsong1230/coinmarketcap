from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.database import SessionLocal
from app.models import User
from app.services import PortfolioService, AlertService
from app.telegram_bot import TelegramBot
from app.config import settings
from app.utils import format_portfolio_message
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
            logger.info(f"포트폴리오 체크 시작: 등록된 사용자 수 = {len(users)}")
            
            if not users:
                logger.warning("등록된 사용자가 없습니다. /start 명령어로 사용자를 등록하세요.")
                return
            
            for user in users:
                try:
                    logger.info(f"사용자 {user.id} (chat_id: {user.telegram_chat_id}) 포트폴리오 확인 중...")
                    portfolio_service = PortfolioService(db)
                    summary = portfolio_service.get_portfolio_summary(user.id)
                    
                    if not summary:
                        logger.warning(f"사용자 {user.id}의 포트폴리오가 설정되지 않았습니다.")
                        continue
                    
                    logger.info(f"사용자 {user.id} 포트폴리오 총액: {summary['total_value']} {user.base_currency}")
                    
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
                    logger.info(f"사용자 {user.id} 알림 확인 결과: {len(alerts)}개 알림 발생")
                    
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
        """3시간마다 포트폴리오 요약 전송"""
        logger.info("=" * 60)
        logger.info("3시간 요약 전송 함수 시작")
        db = SessionLocal()
        
        try:
            users = db.query(User).all()
            logger.info(f"3시간 요약 전송 시작: 등록된 사용자 수 = {len(users)}")
            
            if not users:
                logger.warning("등록된 사용자가 없습니다.")
                return
            
            for user in users:
                try:
                    logger.info(f"사용자 {user.id} (chat_id: {user.telegram_chat_id}) 요약 생성 중...")
                    portfolio_service = PortfolioService(db)
                    summary = portfolio_service.get_portfolio_summary(user.id)
                    
                    if not summary:
                        logger.warning(f"사용자 {user.id}의 포트폴리오가 설정되지 않아 요약을 건너뜁니다.")
                        continue
                    
                    logger.info(f"사용자 {user.id} 요약 생성 완료: 총액 {summary['total_value']} {user.base_currency}")
                    
                    # 포트폴리오 요약 메시지 생성
                    message = format_portfolio_message(
                        total_value=summary['total_value'],
                        base_currency=user.base_currency,
                        items=summary['items'],
                        price_data=summary['price_data']
                    )
                    
                    try:
                        await self.bot.send_message(
                            chat_id=user.telegram_chat_id,
                            text=message
                        )
                        logger.info(f"3시간 요약 전송 완료: user_id={user.id}")
                    except Exception as e:
                        logger.error(f"3시간 요약 전송 실패: user_id={user.id}, error={e}", exc_info=True)
                
                except Exception as e:
                    logger.error(f"사용자 {user.id} 요약 생성 실패: {e}", exc_info=True)
        
        except Exception as e:
            logger.error(f"3시간 요약 스케줄러 실행 오류: {e}", exc_info=True)
        finally:
            db.close()
            logger.info("3시간 요약 전송 함수 종료")
            logger.info("=" * 60)
    
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
        
        # 3시간마다 요약 전송
        self.scheduler.add_job(
            self.send_hourly_summary,
            trigger=IntervalTrigger(hours=3),
            id="hourly_summary",
            replace_existing=True
        )
        logger.info("3시간 요약 스케줄러 시작: 3시간 간격")
        
        self.scheduler.start()


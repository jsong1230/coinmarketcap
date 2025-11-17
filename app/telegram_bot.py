from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import Conflict, TimedOut, NetworkError
from typing import Optional
from app.config import settings
from app.database import SessionLocal
from app.models import User, AlertSettings
from app.services import PortfolioService
from app.utils import format_portfolio_message
import logging
import asyncio
import time

logger = logging.getLogger(__name__)


class TelegramBot:
    """텔레그램 봇 핸들러"""
    
    def __init__(self):
        # 타임아웃 설정 추가 (연결 문제 방지)
        self.application = (
            Application.builder()
            .token(settings.telegram_bot_token)
            .read_timeout(30)
            .write_timeout(30)
            .connect_timeout(30)
            .build()
        )
        self.setup_handlers()
    
    def setup_handlers(self):
        """명령어 핸들러 등록"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("summary", self.summary_command))
        self.application.add_handler(CommandHandler("alerts", self.alerts_command))
        self.application.add_handler(CommandHandler("set_alert", self.set_alert_command))
        self.application.add_handler(CommandHandler("advice", self.advice_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # 에러 핸들러 등록
        self.application.add_error_handler(self.error_handler)
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """에러 핸들러"""
        error = context.error
        
        if isinstance(error, Conflict):
            logger.warning(
                f"봇 충돌 감지: 다른 봇 인스턴스가 실행 중입니다. "
                f"이 오류는 무시됩니다. (다른 프로세스를 종료하거나 잠시 기다려주세요)"
            )
            # Conflict 오류는 무시하고 계속 실행
            return
        elif isinstance(error, (TimedOut, NetworkError)):
            logger.warning(f"네트워크 오류 (재시도됨): {error}")
            return
        else:
            logger.error(f"예상치 못한 오류: {error}", exc_info=error)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """봇 시작 및 사용자 등록"""
        chat_id = str(update.effective_chat.id)
        db = SessionLocal()
        
        try:
            user = db.query(User).filter(User.telegram_chat_id == chat_id).first()
            
            if user:
                await update.message.reply_text(
                    f"안녕하세요! 이미 등록된 사용자입니다.\n"
                    f"사용자 ID: {user.id}\n"
                    f"기준 통화: {user.base_currency}\n\n"
                    f"/help 명령어로 사용 가능한 기능을 확인하세요."
                )
            else:
                # 새 사용자 생성
                new_user = User(
                    telegram_chat_id=chat_id,
                    base_currency="KRW"
                )
                db.add(new_user)
                db.flush()  # ID를 생성하기 위해 flush
                
                # 기본 알림 설정 생성
                alert_settings = AlertSettings(
                    user_id=new_user.id
                )
                db.add(alert_settings)
                db.commit()
                db.refresh(new_user)  # 최신 정보로 새로고침
                
                await update.message.reply_text(
                    "🎉 CryptoWatcher Bot에 오신 것을 환영합니다!\n\n"
                    "다음 단계:\n"
                    "1. CMC API Key를 설정하세요 (/set_cmc_key)\n"
                    "2. 포트폴리오를 등록하세요 (/set_portfolio)\n"
                    "3. 알림 기준을 설정하세요 (/set_alert)\n\n"
                    "/help 명령어로 모든 기능을 확인하세요."
                )
        except Exception as e:
            logger.error(f"start_command 오류: {e}", exc_info=True)
            await update.message.reply_text(
                f"오류가 발생했습니다: {str(e)}\n\n"
                "서버 로그를 확인하거나 관리자에게 문의하세요."
            )
        finally:
            db.close()
    
    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """포트폴리오 요약 조회"""
        chat_id = str(update.effective_chat.id)
        db = SessionLocal()
        
        try:
            user = db.query(User).filter(User.telegram_chat_id == chat_id).first()
            
            if not user:
                await update.message.reply_text("먼저 /start 명령어로 등록해주세요.")
                return
            
            service = PortfolioService(db)
            summary = service.get_portfolio_summary(user.id)
            
            if not summary:
                await update.message.reply_text(
                    "포트폴리오가 설정되지 않았습니다.\n"
                    "포트폴리오를 등록하려면 /set_portfolio 명령어를 사용하세요."
                )
                return
            
            message = format_portfolio_message(
                total_value=summary['total_value'],
                base_currency=user.base_currency,
                items=summary['items'],
                price_data=summary['price_data']
            )
            
            await update.message.reply_text(message)
        except Exception as e:
            logger.error(f"summary_command 오류: {e}")
            await update.message.reply_text("포트폴리오 조회 중 오류가 발생했습니다.")
        finally:
            db.close()
    
    async def alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """현재 알림 설정 조회"""
        chat_id = str(update.effective_chat.id)
        db = SessionLocal()
        
        try:
            user = db.query(User).filter(User.telegram_chat_id == chat_id).first()
            
            if not user:
                await update.message.reply_text("먼저 /start 명령어로 등록해주세요.")
                return
            
            alert_settings = db.query(AlertSettings).filter(AlertSettings.user_id == user.id).first()
            
            if not alert_settings:
                await update.message.reply_text("알림 설정이 없습니다. /set_alert 명령어로 설정하세요.")
                return
            
            message = "🔔 알림 설정\n\n"
            message += f"단일 코인 변동률 임계값: {alert_settings.single_coin_percentage_threshold}%\n"
            if alert_settings.single_coin_absolute_threshold:
                message += f"단일 코인 절대가격 변동: {alert_settings.single_coin_absolute_threshold}\n"
            message += f"포트폴리오 변동률 임계값: {alert_settings.portfolio_percentage_threshold}%\n"
            if alert_settings.portfolio_absolute_threshold:
                message += f"포트폴리오 절대금액 변동: {alert_settings.portfolio_absolute_threshold}\n"
            message += f"최소 알림 간격: {alert_settings.min_notification_interval_minutes}분\n"
            
            await update.message.reply_text(message)
        except Exception as e:
            logger.error(f"alerts_command 오류: {e}")
            await update.message.reply_text("알림 설정 조회 중 오류가 발생했습니다.")
        finally:
            db.close()
    
    async def set_alert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """알림 기준 설정"""
        await update.message.reply_text(
            "알림 설정은 API를 통해 변경할 수 있습니다.\n"
            "자세한 내용은 /help 명령어를 참조하세요."
        )
    
    async def advice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """투자 조언 요청"""
        await update.message.reply_text(
            "📈 투자 조언 기능은 곧 추가될 예정입니다.\n"
            "현재는 포트폴리오 모니터링과 알림 기능을 사용하실 수 있습니다."
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """도움말"""
        help_text = """
🤖 CryptoWatcher Bot 명령어

/start - 봇 시작 및 사용자 등록
/summary - 포트폴리오 요약 조회
/alerts - 현재 알림 설정 조회
/set_alert - 알림 기준 설정 (API 사용)
/advice - 투자 조언 요청
/help - 이 도움말 표시

📡 API 엔드포인트:
- POST /api/users - 사용자 등록
- GET /api/users/me - 내 정보 조회
- POST /api/portfolio - 포트폴리오 항목 추가
- GET /api/portfolio/summary - 포트폴리오 요약
- PUT /api/alerts - 알림 설정 변경

자세한 API 문서는 /docs 엔드포인트를 참조하세요.
        """
        await update.message.reply_text(help_text)
    
    def run(self):
        """봇 실행 (별도 스레드에서 실행)"""
        logger.info("텔레그램 봇 시작...")
        # 새로운 이벤트 루프 생성 (별도 스레드용)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # webhook 삭제 (이전 webhook이 있으면 충돌 발생)
            async def delete_webhook():
                try:
                    await self.application.bot.delete_webhook(drop_pending_updates=True)
                    logger.info("Webhook 삭제 완료")
                    # webhook 삭제 후 잠시 대기 (다른 인스턴스가 종료될 시간 제공)
                    await asyncio.sleep(3)
                except Exception as e:
                    logger.warning(f"Webhook 삭제 중 오류 (무시 가능): {e}")
            
            loop.run_until_complete(delete_webhook())
            
            # run_polling은 무한 루프로 실행되므로 run_until_complete로 감싸면 계속 실행됨
            # stop_signals=None으로 시그널 핸들러 비활성화 (별도 스레드에서는 사용 불가)
            # 에러 핸들러가 Conflict 오류를 처리하므로 여기서는 그냥 실행
            loop.run_until_complete(
                self.application.run_polling(
                    allowed_updates=Update.ALL_TYPES,
                    stop_signals=None,  # 시그널 핸들러 비활성화
                    drop_pending_updates=True
                )
            )
        except Exception as e:
            logger.error(f"텔레그램 봇 실행 중 오류: {e}", exc_info=True)
        finally:
            loop.close()


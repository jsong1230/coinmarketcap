#!/usr/bin/env python3
"""
로컬에서 실행되는 포트폴리오 모니터링 스크립트
APScheduler를 사용하여 주기적으로 포트폴리오를 확인하고 텔레그램 알림을 전송합니다.
"""
import os
import sys
import signal
import logging
import json
import requests
import asyncio
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telegram import Bot

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 환경 변수
CMC_API_KEY = os.getenv("CMC_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE_CURRENCY = os.getenv("BASE_CURRENCY", "KRW")
MONITOR_INTERVAL_HOURS = int(os.getenv("MONITOR_INTERVAL_HOURS", "1"))

# 포트폴리오 설정
DEFAULT_PORTFOLIO = '{"BTC": 4.4744, "ETH": 26.52, "SOL": 100.26, "META": 11325.73}'
PORTFOLIO_JSON = os.getenv("PORTFOLIO_JSON", DEFAULT_PORTFOLIO)

CMC_BASE_URL = "https://pro-api.coinmarketcap.com/v1"

# 로깅 설정
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "monitor.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# PID 파일 경로
PID_FILE = project_root / "monitor.pid"

# 전역 변수
scheduler = None
bot = None


def get_latest_quotes(symbols, convert="USD"):
    """CMC API로 가격 조회"""
    symbols_str = ",".join(symbols)
    url = f"{CMC_BASE_URL}/cryptocurrency/quotes/latest"
    headers = {
        "X-CMC_PRO_API_KEY": CMC_API_KEY,
        "Accept": "application/json"
    }
    params = {
        "symbol": symbols_str,
        "convert": convert
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"CMC API 오류: {e}")
        return None


def parse_quote_data(response_data, symbol, convert="USD"):
    """API 응답에서 가격 데이터 추출"""
    try:
        data = response_data.get("data", {})
        coin_data = data.get(symbol)
        
        if not coin_data:
            return None
        
        if isinstance(coin_data, dict):
            quote = coin_data.get("quote", {}).get(convert, {})
        elif isinstance(coin_data, list) and len(coin_data) > 0:
            quote = coin_data[0].get("quote", {}).get(convert, {})
        else:
            return None
        
        return {
            "symbol": symbol,
            "price": quote.get("price", 0),
            "percent_change_24h": quote.get("percent_change_24h", 0),
            "percent_change_7d": quote.get("percent_change_7d", 0),
        }
    except Exception as e:
        logger.error(f"데이터 파싱 오류: {e}")
        return None


def calculate_portfolio_value(portfolio, price_data):
    """포트폴리오 총 평가액 계산"""
    total_value = 0
    items_summary = []
    
    for symbol, quantity in portfolio.items():
        price_info = price_data.get(symbol)
        if price_info:
            price = price_info.get("price", 0)
            value = quantity * price
            total_value += value
            items_summary.append({
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "value": value,
                "change_24h": price_info.get("percent_change_24h", 0)
            })
    
    return total_value, items_summary


async def send_telegram_message(chat_id, message):
    """텔레그램 메시지 전송"""
    try:
        chat_id_int = int(chat_id)
        sent_message = await bot.send_message(chat_id=chat_id_int, text=message)
        logger.info(f"✅ 텔레그램 메시지 전송 완료 (chat_id={chat_id_int})")
        return True
    except Exception as e:
        logger.error(f"❌ 텔레그램 전송 실패: {e}")
        return False


async def check_and_send_portfolio():
    """포트폴리오 확인 및 텔레그램 전송"""
    logger.info("📊 포트폴리오 모니터링 시작...")
    
    if not CMC_API_KEY:
        logger.error("❌ CMC_API_KEY가 설정되지 않았습니다.")
        return
    
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN이 설정되지 않았습니다.")
        return
    
    if not TELEGRAM_CHAT_ID:
        logger.error("❌ TELEGRAM_CHAT_ID가 설정되지 않았습니다.")
        return
    
    # 포트폴리오 파싱
    try:
        portfolio = json.loads(PORTFOLIO_JSON)
    except json.JSONDecodeError as e:
        logger.error(f"❌ PORTFOLIO_JSON 파싱 실패: {e}")
        return
    
    symbols = list(portfolio.keys())
    logger.info(f"📊 모니터링 대상: {', '.join(symbols)}")
    
    # 가격 조회
    response = get_latest_quotes(symbols, BASE_CURRENCY)
    if not response:
        logger.error("❌ 가격 조회 실패")
        return
    
    # 가격 데이터 파싱
    price_data = {}
    for symbol in symbols:
        price_info = parse_quote_data(response, symbol, BASE_CURRENCY)
        if price_info:
            price_data[symbol] = price_info
    
    if not price_data:
        logger.error("❌ 가격 데이터 없음")
        return
    
    # 포트폴리오 평가액 계산
    total_value, items_summary = calculate_portfolio_value(portfolio, price_data)
    
    # 메시지 생성
    message = f"📊 포트폴리오 요약 ({BASE_CURRENCY})\n"
    message += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    message += f"💰 총 평가액: {total_value:,.0f} {BASE_CURRENCY}\n\n"
    
    for item in items_summary:
        message += f"💵 {item['symbol']}\n"
        message += f"   수량: {item['quantity']:,.6f}\n"
        message += f"   현재가: {item['price']:,.2f} {BASE_CURRENCY}\n"
        message += f"   평가액: {item['value']:,.2f} {BASE_CURRENCY}\n"
        message += f"   24h 변동: {item['change_24h']:+.2f}%\n\n"
    
    # 텔레그램 전송
    await send_telegram_message(TELEGRAM_CHAT_ID, message)
    logger.info("✅ 포트폴리오 모니터링 완료")


def save_pid():
    """PID 파일 저장"""
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))


def remove_pid():
    """PID 파일 삭제"""
    if PID_FILE.exists():
        PID_FILE.unlink()


def signal_handler(signum, frame):
    """시그널 핸들러 (종료 처리)"""
    logger.info("종료 신호 수신, 스케줄러 종료 중...")
    if scheduler:
        scheduler.shutdown()
    remove_pid()
    sys.exit(0)


def main():
    """메인 함수"""
    global scheduler, bot
    
    # 이미 실행 중인지 확인
    if PID_FILE.exists():
        with open(PID_FILE, 'r') as f:
            old_pid = int(f.read().strip())
        try:
            os.kill(old_pid, 0)  # 프로세스가 존재하는지 확인
            logger.error(f"이미 실행 중입니다 (PID: {old_pid})")
            logger.info("종료하려면: python scripts/stop_monitor.py 또는 ./scripts/stop_monitor.sh")
            sys.exit(1)
        except OSError:
            # 프로세스가 없으면 PID 파일 삭제
            remove_pid()
    
    # 환경 변수 확인
    logger.info("🔍 환경 변수 확인:")
    logger.info(f"  CMC_API_KEY: {'✅ 설정됨' if CMC_API_KEY else '❌ 없음'}")
    logger.info(f"  TELEGRAM_BOT_TOKEN: {'✅ 설정됨' if TELEGRAM_BOT_TOKEN else '❌ 없음'}")
    logger.info(f"  TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID if TELEGRAM_CHAT_ID else '❌ 없음'}")
    logger.info(f"  BASE_CURRENCY: {BASE_CURRENCY}")
    logger.info(f"  MONITOR_INTERVAL_HOURS: {MONITOR_INTERVAL_HOURS}")
    logger.info(f"  PORTFOLIO_JSON: {PORTFOLIO_JSON[:50]}..." if len(PORTFOLIO_JSON) > 50 else f"  PORTFOLIO_JSON: {PORTFOLIO_JSON}")
    
    if not all([CMC_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
        logger.error("필수 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    # 봇 초기화
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # 스케줄러 설정
    scheduler = AsyncIOScheduler()
    
    # 즉시 한 번 실행
    scheduler.add_job(
        check_and_send_portfolio,
        trigger=None,
        id="immediate_check",
        replace_existing=True
    )
    
    # 주기적으로 실행
    scheduler.add_job(
        check_and_send_portfolio,
        trigger=IntervalTrigger(hours=MONITOR_INTERVAL_HOURS),
        id="periodic_check",
        replace_existing=True
    )
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # PID 파일 저장
    save_pid()
    
    logger.info(f"🚀 포트폴리오 모니터링 시작 (PID: {os.getpid()})")
    logger.info(f"⏰ 실행 간격: {MONITOR_INTERVAL_HOURS}시간")
    logger.info(f"📝 로그 파일: {log_file}")
    logger.info("종료하려면 Ctrl+C 또는 ./scripts/stop_monitor.sh")
    
    # 스케줄러 시작
    scheduler.start()
    
    try:
        # 무한 대기
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        logger.info("키보드 인터럽트 수신")
    finally:
        scheduler.shutdown()
        remove_pid()
        logger.info("모니터링 종료")


if __name__ == "__main__":
    main()


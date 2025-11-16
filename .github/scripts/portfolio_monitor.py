#!/usr/bin/env python3
"""
GitHub Actions에서 실행되는 포트폴리오 모니터링 스크립트
서버 없이 GitHub Actions만으로 포트폴리오를 모니터링하고 알림을 전송합니다.
"""
import os
import requests
from telegram import Bot
from datetime import datetime
import json
import asyncio

# 환경 변수
CMC_API_KEY = os.getenv("CMC_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "57364261")  # 기본값 설정
BASE_CURRENCY = os.getenv("BASE_CURRENCY", "KRW")

# 포트폴리오 설정 (GitHub Secrets에서 가져오거나 여기에 직접 설정)
# GitHub Secrets에 PORTFOLIO_JSON을 추가하거나 아래에 직접 입력
DEFAULT_PORTFOLIO = '{"BTC": 4.4744, "ETH": 26.52, "SOL": 100.26, "META": 11325.73}'
PORTFOLIO_JSON = os.getenv("PORTFOLIO_JSON", DEFAULT_PORTFOLIO)

CMC_BASE_URL = "https://pro-api.coinmarketcap.com/v1"


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
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"CMC API 오류: {e}")
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
        print(f"데이터 파싱 오류: {e}")
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


async def send_telegram_message(bot, chat_id, message):
    """텔레그램 메시지 전송"""
    try:
        # chat_id를 정수로 변환 시도
        try:
            chat_id_int = int(chat_id)
        except ValueError:
            chat_id_int = chat_id
        
        print(f"   메시지 전송 시도: chat_id={chat_id_int} (type: {type(chat_id_int).__name__})")
        
        # 메시지 전송
        sent_message = await bot.send_message(chat_id=chat_id_int, text=message)
        
        print(f"✅ 텔레그램 메시지 전송 완료!")
        print(f"   메시지 ID: {sent_message.message_id}")
        print(f"   채팅 ID: {sent_message.chat.id}")
        return True
    except Exception as e:
        print(f"❌ 텔레그램 전송 실패: {e}")
        print(f"   오류 타입: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 함수"""
    print("🚀 포트폴리오 모니터링 시작...")
    
    # 환경 변수 확인
    print(f"🔍 환경 변수 확인:")
    print(f"  CMC_API_KEY: {'✅ 설정됨 (' + CMC_API_KEY[:10] + '...)' if CMC_API_KEY else '❌ 없음'}")
    print(f"  TELEGRAM_BOT_TOKEN: {'✅ 설정됨 (' + TELEGRAM_BOT_TOKEN[:10] + '...)' if TELEGRAM_BOT_TOKEN else '❌ 없음'}")
    print(f"  TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID if TELEGRAM_CHAT_ID else '❌ 없음'} (type: {type(TELEGRAM_CHAT_ID).__name__})")
    print(f"  BASE_CURRENCY: {BASE_CURRENCY}")
    print(f"  PORTFOLIO_JSON: {PORTFOLIO_JSON[:50]}..." if len(PORTFOLIO_JSON) > 50 else f"  PORTFOLIO_JSON: {PORTFOLIO_JSON}")
    print()
    
    # GitHub Actions 환경 확인
    is_github_actions = os.getenv("GITHUB_ACTIONS") == "true"
    print(f"🌐 실행 환경: {'GitHub Actions' if is_github_actions else '로컬'}")
    if is_github_actions:
        print(f"  Workflow: {os.getenv('GITHUB_WORKFLOW', 'N/A')}")
        print(f"  Run ID: {os.getenv('GITHUB_RUN_ID', 'N/A')}")
    print()
    
    if not CMC_API_KEY:
        print("❌ CMC_API_KEY가 설정되지 않았습니다.")
        return
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN이 설정되지 않았습니다.")
        return
    
    if not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_CHAT_ID가 설정되지 않았습니다.")
        return
    
    # 포트폴리오 파싱
    try:
        portfolio = json.loads(PORTFOLIO_JSON)
    except json.JSONDecodeError:
        print(f"❌ PORTFOLIO_JSON 파싱 실패: {PORTFOLIO_JSON}")
        return
    
    symbols = list(portfolio.keys())
    print(f"📊 모니터링 대상: {', '.join(symbols)}")
    
    # 가격 조회
    response = get_latest_quotes(symbols, BASE_CURRENCY)
    if not response:
        print("❌ 가격 조회 실패")
        return
    
    # 가격 데이터 파싱
    price_data = {}
    for symbol in symbols:
        price_info = parse_quote_data(response, symbol, BASE_CURRENCY)
        if price_info:
            price_data[symbol] = price_info
    
    if not price_data:
        print("❌ 가격 데이터 없음")
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
    print(f"📤 텔레그램 메시지 전송 시도...")
    print(f"   Chat ID: {TELEGRAM_CHAT_ID} (type: {type(TELEGRAM_CHAT_ID).__name__})")
    print(f"   메시지 길이: {len(message)} 글자")
    print(f"   메시지 미리보기: {message[:100]}...")
    
    async def send_message():
        try:
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            print(f"   봇 초기화 완료")
            
            # 봇 정보 확인
            bot_info = await bot.get_me()
            print(f"   봇 이름: {bot_info.first_name} (@{bot_info.username})")
            print(f"   봇 ID: {bot_info.id}")
            
            # Chat 정보 확인 시도
            try:
                chat_id_int = int(TELEGRAM_CHAT_ID)
                print(f"   채팅 정보 확인 시도: chat_id={chat_id_int}")
                chat = await bot.get_chat(chat_id_int)
                print(f"   ✅ 채팅 정보 확인 성공:")
                print(f"     - Chat ID: {chat.id}")
                print(f"     - 타입: {chat.type}")
                print(f"     - 이름: {chat.first_name or ''} {chat.last_name or ''}")
                print(f"     - 사용자명: @{chat.username or '없음'}")
            except Exception as chat_error:
                print(f"   ⚠️ 채팅 정보 확인 실패:")
                print(f"     오류: {chat_error}")
                print(f"     오류 타입: {type(chat_error).__name__}")
                print(f"     ⚠️ 이 경우 메시지 전송이 실패할 수 있습니다.")
                print(f"     해결: 텔레그램에서 봇에게 먼저 /start 메시지를 보내세요.")
            
            # 메시지 전송
            print(f"   메시지 전송 시작...")
            result = await send_telegram_message(bot, TELEGRAM_CHAT_ID, message)
            return result
        except Exception as e:
            print(f"❌ 텔레그램 전송 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    try:
        result = asyncio.run(send_message())
        if result:
            print("✅ 모니터링 완료")
        else:
            print("⚠️ 모니터링 완료 (전송 실패)")
    except Exception as e:
        print(f"❌ 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


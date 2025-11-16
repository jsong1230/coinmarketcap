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

# 환경 변수
CMC_API_KEY = os.getenv("CMC_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE_CURRENCY = os.getenv("BASE_CURRENCY", "KRW")

# 포트폴리오 설정 (GitHub Secrets에서 가져오거나 여기에 직접 설정)
# GitHub Secrets에 PORTFOLIO_JSON을 추가하거나 아래에 직접 입력
PORTFOLIO_JSON = os.getenv("PORTFOLIO_JSON", '{"BTC": 4.4744, "ETH": 26.52, "SOL": 100.26, "META": 11325.73}')

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


def send_telegram_message(bot, chat_id, message):
    """텔레그램 메시지 전송"""
    try:
        bot.send_message(chat_id=chat_id, text=message)
        print("✅ 텔레그램 메시지 전송 완료")
        return True
    except Exception as e:
        print(f"❌ 텔레그램 전송 실패: {e}")
        return False


def main():
    """메인 함수"""
    print("🚀 포트폴리오 모니터링 시작...")
    
    # 환경 변수 확인
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
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    send_telegram_message(bot, TELEGRAM_CHAT_ID, message)
    
    print("✅ 모니터링 완료")


if __name__ == "__main__":
    main()


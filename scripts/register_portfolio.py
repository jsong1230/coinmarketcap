#!/usr/bin/env python3
"""
포트폴리오 등록 스크립트
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def register_user(telegram_chat_id: str):
    """사용자 등록"""
    url = f"{BASE_URL}/api/users"
    data = {
        "telegram_chat_id": telegram_chat_id,
        "base_currency": "USD"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"✅ 사용자 등록 완료: {telegram_chat_id}")
            return True
        elif response.status_code == 400:
            print(f"ℹ️  이미 등록된 사용자입니다: {telegram_chat_id}")
            return True
        else:
            print(f"❌ 사용자 등록 실패: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        print("   실행 명령: python run.py 또는 ./start_server.sh")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def add_portfolio_item(telegram_chat_id: str, symbol: str, quantity: float):
    """포트폴리오 항목 추가"""
    url = f"{BASE_URL}/api/portfolio"
    params = {"telegram_chat_id": telegram_chat_id}
    data = {
        "symbol": symbol,
        "quantity": quantity
    }
    
    try:
        response = requests.post(url, params=params, json=data)
        if response.status_code == 200:
            print(f"✅ {symbol}: {quantity} 추가 완료")
            return True
        else:
            print(f"❌ {symbol} 추가 실패: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def get_portfolio_summary(telegram_chat_id: str):
    """포트폴리오 요약 조회"""
    url = f"{BASE_URL}/api/portfolio/summary"
    params = {"telegram_chat_id": telegram_chat_id}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ 포트폴리오 조회 실패: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("사용법: python register_portfolio.py <TELEGRAM_CHAT_ID>")
        print("\n텔레그램 chat_id 확인 방법:")
        print("1. 텔레그램에서 @userinfobot에게 메시지 보내기")
        print("2. 또는 봇과 대화 시작 후 확인")
        sys.exit(1)
    
    telegram_chat_id = sys.argv[1]
    
    print("=" * 50)
    print("포트폴리오 등록 시작")
    print("=" * 50)
    
    # 1. 사용자 등록
    if not register_user(telegram_chat_id):
        sys.exit(1)
    
    # 2. 포트폴리오 항목 추가
    portfolio_items = [
        ("BTC", 4.4744),
        ("ETH", 26.52),
        ("SOL", 100.26),
        ("META", 11325.73)
    ]
    
    print("\n포트폴리오 항목 추가 중...")
    for symbol, quantity in portfolio_items:
        add_portfolio_item(telegram_chat_id, symbol, quantity)
    
    # 3. 포트폴리오 요약 조회
    print("\n" + "=" * 50)
    print("포트폴리오 요약")
    print("=" * 50)
    summary = get_portfolio_summary(telegram_chat_id)
    
    if summary:
        print(f"\n총 평가액: ${summary['total_value']:,.2f} {summary['base_currency']}")
        print("\n보유 자산:")
        for item in summary['items']:
            symbol = item['symbol']
            quantity = item['quantity']
            price_data = summary['price_data'].get(symbol, {})
            price = price_data.get('price', 0)
            value = quantity * price
            change_24h = price_data.get('percent_change_24h', 0)
            
            print(f"  {symbol}:")
            print(f"    수량: {quantity:,.6f}")
            print(f"    현재가: ${price:,.2f}")
            print(f"    평가액: ${value:,.2f}")
            print(f"    24h 변동: {change_24h:+.2f}%")
            print()
    
    print("=" * 50)
    print("✅ 포트폴리오 등록 완료!")
    print("=" * 50)

if __name__ == "__main__":
    main()


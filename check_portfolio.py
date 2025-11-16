#!/usr/bin/env python3
"""포트폴리오 계산 확인 스크립트"""
import requests
import json

BASE_URL = "http://localhost:8000"
CHAT_ID = "57364261"

response = requests.get(f"{BASE_URL}/api/portfolio/summary?telegram_chat_id={CHAT_ID}")
data = response.json()

items = data['items']
price_data = data['price_data']

print("=" * 60)
print("포트폴리오 계산 확인")
print("=" * 60)
print(f"\n총 항목 수: {len(items)}개")
print(f"API 총 평가액: {data['total_value']:,.0f} {data['base_currency']}\n")

# 중복 확인
from collections import Counter
counts = Counter((item['symbol'], item['quantity']) for item in items)
duplicates = {k: v for k, v in counts.items() if v > 1}

if duplicates:
    print("⚠️  중복 항목 발견:")
    for (symbol, qty), count in duplicates.items():
        print(f"  {symbol}: {qty} x {count}회")
    print()

# 개별 계산
print("개별 자산 계산:")
total_calculated = 0
unique_items = {}

for item in items:
    symbol = item['symbol']
    qty = item['quantity']
    price = price_data.get(symbol, {}).get('price', 0)
    value = qty * price
    
    if symbol not in unique_items:
        unique_items[symbol] = {'quantity': 0, 'value': 0}
    
    unique_items[symbol]['quantity'] += qty
    unique_items[symbol]['value'] += value
    total_calculated += value

for symbol, data in unique_items.items():
    price = price_data.get(symbol, {}).get('price', 0)
    print(f"  {symbol}:")
    print(f"    수량: {data['quantity']:,.6f}")
    print(f"    현재가: {price:,.0f} {data['base_currency']}")
    print(f"    평가액: {data['value']:,.0f} {data['base_currency']}")
    print()

print("=" * 60)
print(f"계산된 총액: {total_calculated:,.0f} {data['base_currency']}")
print(f"API 총액: {data['total_value']:,.0f} {data['base_currency']}")
print(f"차이: {abs(total_calculated - data['total_value']):,.0f} {data['base_currency']}")
print("=" * 60)


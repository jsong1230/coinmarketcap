#!/usr/bin/env python3
"""
포트폴리오 모니터링 스크립트 테스트 (로컬)
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수
CMC_API_KEY = os.getenv("CMC_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "57364261")
BASE_CURRENCY = os.getenv("BASE_CURRENCY", "KRW")
PORTFOLIO_JSON = os.getenv("PORTFOLIO_JSON", '{"BTC": 4.4744, "ETH": 26.52, "SOL": 100.26, "META": 11325.73}')

print("=" * 60)
print("포트폴리오 모니터링 테스트")
print("=" * 60)
print()

# 환경 변수 확인
print("🔍 환경 변수 확인:")
print(f"  CMC_API_KEY: {'✅ 설정됨' if CMC_API_KEY else '❌ 없음'}")
print(f"  TELEGRAM_BOT_TOKEN: {'✅ 설정됨' if TELEGRAM_BOT_TOKEN else '❌ 없음'}")
print(f"  TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")
print(f"  BASE_CURRENCY: {BASE_CURRENCY}")
print(f"  PORTFOLIO_JSON: {PORTFOLIO_JSON}")
print()

if not CMC_API_KEY or not TELEGRAM_BOT_TOKEN:
    print("❌ 필수 환경 변수가 설정되지 않았습니다.")
    print("   .env 파일을 확인하거나 환경 변수를 설정하세요.")
    sys.exit(1)

# 스크립트 실행
sys.path.insert(0, '.github/scripts')
from portfolio_monitor import main

print()
print("=" * 60)
print("스크립트 실행 중...")
print("=" * 60)
print()

try:
    main()
    print()
    print("=" * 60)
    print("✅ 테스트 완료")
    print("=" * 60)
except Exception as e:
    print()
    print("=" * 60)
    print(f"❌ 오류 발생: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)


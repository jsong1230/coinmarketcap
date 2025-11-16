#!/usr/bin/env python3
"""
CryptoWatcher Bot 실행 스크립트
"""
import os
import sys
from pathlib import Path

# .env 파일이 없으면 생성 안내
env_file = Path(".env")
if not env_file.exists():
    print("⚠️  .env 파일이 없습니다.")
    print("\n다음 내용으로 .env 파일을 생성해주세요:\n")
    print("CMC_API_KEY=your_cmc_api_key_here")
    print("TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here")
    print("DATABASE_URL=sqlite:///./cryptowatcher.db")
    print("HOST=0.0.0.0")
    print("PORT=8000")
    print("SCHEDULER_INTERVAL_MINUTES=5")
    print("\n또는 환경 변수로 직접 설정할 수 있습니다.")
    sys.exit(1)

# 환경 변수 확인
required_vars = ["CMC_API_KEY", "TELEGRAM_BOT_TOKEN"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"⚠️  필수 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
    sys.exit(1)

# uvicorn으로 서버 실행
if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    
    print("🚀 CryptoWatcher Bot 시작 중...")
    print(f"📡 서버 주소: http://{settings.host}:{settings.port}")
    print(f"📚 API 문서: http://{settings.host}:{settings.port}/docs")
    print(f"⏰ 스케줄러 간격: {settings.scheduler_interval_minutes}분")
    print("\n서버를 중지하려면 Ctrl+C를 누르세요.\n")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )


#!/bin/bash

cd /Users/joohansong/dev/coinmarketcap
source venv/bin/activate

echo "🚀 CryptoWatcher Bot 서버 시작 중..."
echo "📡 서버 주소: http://localhost:8000"
echo "📚 API 문서: http://localhost:8000/docs"
echo "⏰ 스케줄러 간격: 5분"
echo ""
echo "서버를 중지하려면 Ctrl+C를 누르세요."
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


#!/bin/bash

echo "🔧 CryptoWatcher Bot 설정 중..."

# 가상환경 확인 및 생성
if [ ! -d "venv" ]; then
    echo "📦 가상환경 생성 중..."
    python3.11 -m venv venv
fi

# 가상환경 활성화
echo "✅ 가상환경 활성화 중..."
source venv/bin/activate

# 의존성 설치
echo "📥 의존성 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다."
    echo ""
    echo "다음 내용으로 .env 파일을 생성해주세요:"
    echo ""
    echo "CMC_API_KEY=your_cmc_api_key_here"
    echo "TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here"
    echo "DATABASE_URL=sqlite:///./cryptowatcher.db"
    echo "HOST=0.0.0.0"
    echo "PORT=8000"
    echo "SCHEDULER_INTERVAL_MINUTES=5"
    echo ""
    exit 1
fi

# 데이터베이스 초기화
echo "🗄️  데이터베이스 초기화 중..."
alembic upgrade head

echo ""
echo "✅ 설정 완료!"
echo ""
echo "서버를 실행하려면:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "또는:"
echo "  uvicorn app.main:app --reload"


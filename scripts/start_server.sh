#!/bin/bash

# 스크립트가 있는 디렉토리에서 프로젝트 루트로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# 가상환경 활성화
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ 가상환경을 찾을 수 없습니다. 먼저 'python3 -m venv venv'를 실행하세요."
    exit 1
fi

echo "🚀 CryptoWatcher Bot 서버 시작 중..."
echo "📡 서버 주소: http://localhost:8000"
echo "📚 API 문서: http://localhost:8000/docs"
echo "⏰ 스케줄러 간격: 5분"
echo ""
echo "서버를 중지하려면 Ctrl+C를 누르세요."
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


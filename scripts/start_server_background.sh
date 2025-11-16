#!/bin/bash
# 서버를 백그라운드로 시작하는 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"
PID_FILE="$PROJECT_ROOT/server.pid"
LOG_DIR="$PROJECT_ROOT/logs"

# 가상환경 활성화
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
else
    echo "❌ 가상환경을 찾을 수 없습니다: $VENV_PATH"
    echo "먼저 'python3 -m venv venv'를 실행하세요."
    exit 1
fi

# 로그 디렉토리 생성
mkdir -p "$LOG_DIR"

# 이미 실행 중인지 확인
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️ 서버가 이미 실행 중입니다 (PID: $OLD_PID)"
        echo "종료하려면: ./scripts/stop_server.sh"
        exit 1
    else
        echo "🧹 이전 PID 파일 정리 중..."
        rm -f "$PID_FILE"
    fi
fi

# 환경 변수 확인
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "⚠️ .env 파일을 찾을 수 없습니다."
    echo "프로젝트 루트에 .env 파일을 생성하세요."
fi

# 백그라운드로 실행
echo "🚀 CryptoWatcher Bot 서버 시작 중..."
cd "$PROJECT_ROOT"

# nohup으로 실행하여 터미널 종료 후에도 계속 실행되도록 함
# --reload 옵션 제거 (백그라운드 실행 시 불필요)
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$LOG_DIR/server.log" 2>&1 &

NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

# 잠시 대기 후 프로세스 확인
sleep 3

if ps -p "$NEW_PID" > /dev/null 2>&1; then
    echo "✅ 서버가 시작되었습니다 (PID: $NEW_PID)"
    echo "📡 서버 주소: http://localhost:8000"
    echo "📚 API 문서: http://localhost:8000/docs"
    echo "📝 로그 파일: $LOG_DIR/server.log"
    echo "📊 로그 확인: tail -f $LOG_DIR/server.log"
    echo "🛑 종료: ./scripts/stop_server.sh"
    echo "📈 상태 확인: ./scripts/status_server.sh"
else
    echo "❌ 서버 시작 실패"
    echo "로그 확인: cat $LOG_DIR/server.log"
    rm -f "$PID_FILE"
    exit 1
fi


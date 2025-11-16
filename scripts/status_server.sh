#!/bin/bash
# 서버 상태를 확인하는 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$PROJECT_ROOT/server.pid"
LOG_DIR="$PROJECT_ROOT/logs"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️ 서버가 실행 중이 아닙니다."
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ 서버가 실행 중입니다 (PID: $PID)"
    echo "📡 서버 주소: http://localhost:8000"
    echo "📚 API 문서: http://localhost:8000/docs"
    
    # 포트 확인
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✅ 포트 8000에서 리스닝 중"
    else
        echo "⚠️ 포트 8000에서 리스닝하지 않습니다"
    fi
    
    if [ -f "$LOG_DIR/server.log" ]; then
        echo ""
        echo "📝 최근 로그 (마지막 10줄):"
        echo "---"
        tail -n 10 "$LOG_DIR/server.log"
        echo "---"
        echo ""
        echo "전체 로그 확인: tail -f $LOG_DIR/server.log"
    fi
else
    echo "⚠️ 서버 프로세스가 실행 중이 아닙니다 (PID: $PID)"
    echo "🧹 PID 파일 정리 중..."
    rm -f "$PID_FILE"
    exit 1
fi


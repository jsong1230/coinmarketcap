#!/bin/bash
# 포트폴리오 모니터링 상태 확인 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$PROJECT_ROOT/monitor.pid"
LOG_FILE="$PROJECT_ROOT/logs/monitor.log"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ 모니터링이 실행 중이 아닙니다."
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ 모니터링 실행 중 (PID: $PID)"
    echo ""
    echo "프로세스 정보:"
    ps -p "$PID" -o pid,ppid,cmd,etime,pcpu,pmem
    echo ""
    if [ -f "$LOG_FILE" ]; then
        echo "최근 로그 (마지막 10줄):"
        echo "---"
        tail -n 10 "$LOG_FILE"
    fi
else
    echo "❌ 프로세스가 실행 중이 아닙니다 (PID: $PID)"
    echo "🧹 PID 파일 정리 중..."
    rm -f "$PID_FILE"
    exit 1
fi


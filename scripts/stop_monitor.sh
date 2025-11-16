#!/bin/bash
# 포트폴리오 모니터링을 중지하는 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$PROJECT_ROOT/monitor.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️ 실행 중인 모니터링 프로세스를 찾을 수 없습니다."
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "⚠️ 프로세스가 실행 중이 아닙니다 (PID: $PID)"
    echo "🧹 PID 파일 정리 중..."
    rm -f "$PID_FILE"
    exit 1
fi

echo "🛑 모니터링 프로세스 종료 중... (PID: $PID)"
kill "$PID"

# 프로세스가 종료될 때까지 대기
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ 모니터링이 종료되었습니다."
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# 강제 종료
if ps -p "$PID" > /dev/null 2>&1; then
    echo "⚠️ 정상 종료 실패, 강제 종료 중..."
    kill -9 "$PID"
    sleep 1
    rm -f "$PID_FILE"
    echo "✅ 강제 종료 완료"
else
    rm -f "$PID_FILE"
    echo "✅ 모니터링이 종료되었습니다."
fi


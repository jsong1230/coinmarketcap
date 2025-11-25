#!/bin/bash
# Git hooks 설치 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GITHOOKS_DIR="$PROJECT_ROOT/.githooks"
GIT_HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

echo "🔧 Git hooks 설치 중..."

if [ ! -d "$GITHOOKS_DIR" ]; then
    echo "❌ .githooks 디렉토리를 찾을 수 없습니다."
    exit 1
fi

# .git/hooks 디렉토리가 없으면 생성
if [ ! -d "$GIT_HOOKS_DIR" ]; then
    mkdir -p "$GIT_HOOKS_DIR"
fi

# pre-commit hook 복사
if [ -f "$GITHOOKS_DIR/pre-commit" ]; then
    cp "$GITHOOKS_DIR/pre-commit" "$GIT_HOOKS_DIR/pre-commit"
    chmod +x "$GIT_HOOKS_DIR/pre-commit"
    echo "✅ pre-commit hook 설치 완료"
else
    echo "⚠️  pre-commit hook을 찾을 수 없습니다."
fi

echo "✅ Git hooks 설치가 완료되었습니다."
echo ""
echo "이제 커밋 전에 README.md와 CHANGELOG.md 업데이트를 확인합니다."



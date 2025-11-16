#!/bin/bash
# Git History에서 Secret 제거 스크립트

echo "⚠️  Git History에서 Secret 제거를 시작합니다..."
echo "이 작업은 되돌릴 수 없습니다!"
echo ""
read -p "계속하시겠습니까? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "취소되었습니다."
    exit 1
fi

# git-filter-repo가 없으면 설치
if ! command -v git-filter-repo &> /dev/null; then
    echo "git-filter-repo 설치 중..."
    pip3 install git-filter-repo
fi

# 백업 브랜치 생성
echo "백업 브랜치 생성 중..."
git branch backup-before-secret-removal

# CMC API Key 제거
echo "CMC API Key 제거 중..."
git filter-repo --replace-text <(echo "0b6290bfe327458db0e403288789ee99==>REMOVED_SECRET")

# Telegram Token 제거
echo "Telegram Token 제거 중..."
git filter-repo --replace-text <(echo "8362947773:AAGGAg4OhA25Dji78aFIkY3y_U0Xe9Okzw4==>REMOVED_SECRET")

echo ""
echo "✅ Secret 제거 완료!"
echo ""
echo "다음 단계:"
echo "1. git log로 확인: git log --all"
echo "2. Force push (주의!): git push origin --force --all"
echo "3. 백업 브랜치 확인: git branch"


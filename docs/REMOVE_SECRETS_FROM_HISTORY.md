# Git History에서 Secret 제거 가이드

## 현재 상황
최근 커밋(51d0598, 3a7a5e5)에서 이미 secret을 제거했습니다.
하지만 이전 커밋 히스토리에는 여전히 secret이 남아있을 수 있습니다.

## 방법 1: BFG Repo-Cleaner 사용 (권장)

### 1. BFG 설치
```bash
brew install bfg
# 또는
# https://rtyley.github.io/bfg-repo-cleaner/ 에서 다운로드
```

### 2. Secret 제거
```bash
# 저장소 클론 (bare)
cd /tmp
git clone --mirror https://github.com/jsong1230/coinmarketcap.git

# Secret 제거
bfg --replace-text <(echo "REMOVED_SECRET==>REMOVED") coinmarketcap.git
bfg --replace-text <(echo "REMOVED_SECRET==>REMOVED") coinmarketcap.git

# 히스토리 정리
cd coinmarketcap.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push --force
```

## 방법 2: Fresh Clone에서 git-filter-repo 사용

### 1. Fresh Clone
```bash
cd /tmp
git clone https://github.com/jsong1230/coinmarketcap.git coinmarketcap-clean
cd coinmarketcap-clean
```

### 2. Secret 제거
```bash
# Secret 제거
git filter-repo --replace-text <(echo "REMOVED_SECRET==>REMOVED_SECRET")
git filter-repo --replace-text <(echo "REMOVED_SECRET==>REMOVED_SECRET")

# Force push
git push origin --force --all
```

## 방법 3: 새 저장소로 이전 (가장 안전)

### 1. 새 저장소 생성
- GitHub에서 새 private 저장소 생성

### 2. 현재 코드만 푸시
```bash
cd /Users/joohansong/dev/coinmarketcap
git remote set-url origin <새_저장소_URL>
git push -u origin main --force
```

## 방법 4: API 키/토큰 교체 (가장 빠름)

Git history를 수정하는 대신:
1. **CMC API Key 교체**
   - CoinMarketCap에서 새 API 키 발급
   - 기존 키 무효화

2. **Telegram Bot Token 교체**
   - @BotFather에서 새 토큰 발급
   - 기존 토큰 무효화

3. **환경 변수 업데이트**
   - `.env` 파일 업데이트
   - GitHub Secrets 업데이트

## ⚠️ 주의사항

1. **Force Push는 위험합니다**
   - 팀원과 협의 후 진행
   - 백업 필수

2. **GitHub는 이미 노출된 정보를 캐시할 수 있습니다**
   - 완전한 제거는 어려울 수 있음
   - API 키/토큰 교체가 더 안전

3. **백업 확인**
   - `backup-before-secret-removal` 브랜치 생성됨
   - 문제 발생 시 복구 가능

## 추천 방법

**가장 빠르고 안전한 방법: API 키/토큰 교체**
- Git history 수정은 복잡하고 위험함
- 새 키 발급이 더 빠르고 안전함


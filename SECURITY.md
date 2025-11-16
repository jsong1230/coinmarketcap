# 보안 가이드

## ⚠️ 중요: Secret 관리

**절대 GitHub에 실제 API 키나 토큰을 커밋하지 마세요!**

## 이미 커밋된 Secret 제거 방법

만약 실수로 secret을 커밋했다면:

### 1. Git History에서 제거
```bash
# git-filter-repo 설치 (권장)
pip install git-filter-repo

# 또는 BFG Repo-Cleaner 사용
# https://rtyley.github.io/bfg-repo-cleaner/
```

### 2. Secret 제거 (git-filter-repo 사용)
```bash
# CMC API Key 제거
git filter-repo --replace-text <(echo "REMOVED_SECRET==>REMOVED")

# Telegram Token 제거
git filter-repo --replace-text <(echo "REMOVED_SECRET==>REMOVED")
```

### 3. Force Push (주의!)
```bash
git push origin --force --all
```

⚠️ **주의**: Force push는 팀과 협의 후 진행하세요!

## 올바른 Secret 관리 방법

### ✅ DO (해야 할 것)
1. `.env` 파일 사용 (`.gitignore`에 포함됨)
2. GitHub Secrets 사용 (Actions용)
3. 환경 변수 사용
4. `.env.example` 파일에 placeholder만 포함

### ❌ DON'T (하지 말아야 할 것)
1. 코드에 하드코딩
2. 문서에 실제 secret 포함
3. 커밋 메시지에 secret 포함
4. 공개 저장소에 `.env` 파일 커밋

## 현재 보안 상태

✅ `.env` 파일은 `.gitignore`에 포함되어 커밋되지 않음
✅ 코드에는 secret이 하드코딩되지 않음
✅ 문서에서 실제 secret 제거 완료

## Secret 교체 필요 시

만약 secret이 노출되었다면:
1. 즉시 해당 API 키/토큰을 무효화
2. 새로운 키/토큰 발급
3. `.env` 파일 업데이트
4. GitHub Secrets 업데이트


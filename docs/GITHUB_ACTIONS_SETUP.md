# GitHub Actions 설정 가이드

## 1. GitHub 저장소 생성 및 푸시

### 저장소 생성
1. GitHub에서 새 저장소 생성 (예: `coinmarketcap`)
2. 저장소 URL 확인

### 로컬에서 푸시
```bash
# 원격 저장소 추가
git remote add origin https://github.com/사용자명/coinmarketcap.git

# 또는 SSH 사용
git remote add origin git@github.com:사용자명/coinmarketcap.git

# 푸시
git push -u origin main
```

## 2. GitHub Secrets 설정

GitHub Actions에서 테스트를 실행하려면 Secrets를 설정해야 합니다.

### Secrets 설정 방법:
1. GitHub 저장소 페이지로 이동
2. **Settings** → **Secrets and variables** → **Actions** 클릭
3. **New repository secret** 클릭
4. 다음 Secrets 추가:

#### 필수 Secrets:
- `CMC_API_KEY`: CoinMarketCap API 키
  - 값: `your_cmc_api_key_here` (실제 API 키 입력)
  
- `TELEGRAM_BOT_TOKEN`: 텔레그램 봇 토큰
  - 값: `your_telegram_bot_token_here` (실제 토큰 입력)

### Secrets 추가 후:
- GitHub Actions가 자동으로 실행됩니다
- `push` 또는 `pull_request` 이벤트 발생 시 CI가 트리거됩니다

## 3. GitHub Actions 확인

### Actions 탭에서 확인:
1. GitHub 저장소의 **Actions** 탭 클릭
2. 워크플로우 실행 상태 확인
3. 각 단계의 로그 확인

### CI 실행 조건:
- `main` 또는 `develop` 브랜치에 push
- `main` 또는 `develop` 브랜치로 pull request

## 4. CI 워크플로우 내용

현재 CI는 다음을 수행합니다:
- ✅ Python 3.11, 3.12 환경에서 테스트
- ✅ 의존성 설치
- ✅ pytest로 테스트 실행
- ✅ 코드 포맷팅 체크 (black)

## 5. 문제 해결

### Secrets가 설정되지 않았을 때:
- 테스트는 기본값(`test_key`, `test_token`)으로 실행됩니다
- 실제 API 호출이 필요한 테스트는 스킵될 수 있습니다

### 테스트 실패 시:
- Actions 탭에서 로그 확인
- 로컬에서 `pytest tests/ -v` 실행하여 재현
- 필요시 테스트 코드 수정


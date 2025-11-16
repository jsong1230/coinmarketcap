# GitHub Actions로 포트폴리오 모니터링 (서버 없이)

서버를 운영하지 않고 GitHub Actions만으로 포트폴리오를 모니터링하고 알림을 받을 수 있습니다.

## 설정 방법

### 1. GitHub Secrets 설정

저장소 → **Settings** → **Secrets and variables** → **Actions**에서 다음 Secrets 추가:

#### 필수 Secrets:
- `CMC_API_KEY`: CoinMarketCap API 키
- `TELEGRAM_BOT_TOKEN`: 텔레그램 봇 토큰
- `TELEGRAM_CHAT_ID`: 텔레그램 chat ID (예: `57364261`)
- `PORTFOLIO_JSON`: 포트폴리오 JSON (예: `{"BTC": 4.4744, "ETH": 26.52, "SOL": 100.26, "META": 11325.73}`)

#### 선택적 Secrets:
- `BASE_CURRENCY`: 기본 통화 (기본값: `KRW`, `USD` 등 가능)

### 2. 워크플로우 확인

`.github/workflows/portfolio_monitor.yml` 파일이 자동으로 생성됩니다.

### 3. 실행

- **자동 실행**: 매시간 정각 (UTC 기준)
- **수동 실행**: Actions 탭 → "Portfolio Monitor" → "Run workflow"

## 장점

✅ **서버 불필요**: 별도 서버 운영 없이 GitHub에서 실행
✅ **무료**: GitHub Actions 무료 티어 사용
✅ **자동화**: 1시간마다 자동 실행
✅ **간단**: 설정만 하면 바로 사용 가능

## 제한사항

⚠️ **GitHub Actions 무료 티어 제한**:
- 월 2,000분 실행 시간
- 1시간마다 실행 시: 약 720분/월 (충분함)
- 동시 실행 작업 수 제한

⚠️ **기능 제한**:
- 데이터베이스 저장 불가 (매번 새로 조회)
- 이전 가격과 비교한 알림 기능 제한적
- 복잡한 알림 로직 구현 어려움

## 서버 vs GitHub Actions 비교

| 기능 | 서버 | GitHub Actions |
|------|------|----------------|
| 24시간 실행 | ✅ | ⚠️ 스케줄에 따라 |
| 데이터베이스 | ✅ | ❌ |
| 복잡한 알림 로직 | ✅ | ⚠️ 제한적 |
| 비용 | 💰 서버 비용 | ✅ 무료 |
| 설정 복잡도 | ⚠️ 복잡 | ✅ 간단 |
| 유지보수 | ⚠️ 필요 | ✅ 자동 |

## 추천 사용 사례

### GitHub Actions 사용 추천:
- 간단한 포트폴리오 모니터링
- 정기적인 요약 보고
- 서버 운영을 원하지 않는 경우

### 서버 사용 추천:
- 복잡한 알림 로직 필요
- 실시간 모니터링 필요
- 데이터베이스 저장 필요
- 사용자별 설정 관리 필요

## 포트폴리오 업데이트

포트폴리오를 변경하려면:
1. GitHub Secrets → `PORTFOLIO_JSON` 수정
2. 또는 `.github/scripts/portfolio_monitor.py` 파일의 기본값 수정

## 문제 해결

### 알림이 오지 않을 때:
1. Actions 탭에서 워크플로우 실행 확인
2. Secrets 설정 확인
3. 로그에서 오류 메시지 확인

### 실행 실패 시:
- Actions 탭 → 워크플로우 실행 → 로그 확인
- Secrets가 올바르게 설정되었는지 확인


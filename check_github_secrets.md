# GitHub Secrets 확인 가이드

## 필수 Secrets 확인

저장소 → **Settings** → **Secrets and variables** → **Actions**에서 다음이 모두 설정되어 있는지 확인:

### 1. CMC_API_KEY
- **이름**: `CMC_API_KEY`
- **값**: CoinMarketCap API 키
- **확인**: 값이 설정되어 있고 비어있지 않은지 확인

### 2. TELEGRAM_BOT_TOKEN
- **이름**: `TELEGRAM_BOT_TOKEN`
- **값**: 텔레그램 봇 토큰 (예: `8362947773:AAGGAg4OhA25Dji78aFIkY3y_U0Xe9Okzw4`)
- **확인**: `:` 문자가 포함되어 있는지 확인

### 3. TELEGRAM_CHAT_ID ⚠️ 중요
- **이름**: `TELEGRAM_CHAT_ID`
- **값**: `57364261` (숫자만, 따옴표 없이)
- **확인**: 
  - ✅ 올바른 예: `57364261`
  - ❌ 잘못된 예: `"57364261"`, `'57364261'`, `57364261 (JooHan)`

### 4. BASE_CURRENCY (선택)
- **이름**: `BASE_CURRENCY`
- **값**: `KRW` 또는 `USD`
- **기본값**: `KRW` (설정하지 않아도 됨)

### 5. PORTFOLIO_JSON (선택)
- **이름**: `PORTFOLIO_JSON`
- **값**: `{"BTC": 4.4744, "ETH": 26.52, "SOL": 100.26, "META": 11325.73}`
- **기본값**: 위 값 (설정하지 않아도 됨)

## Secrets 설정 방법

1. 저장소 → **Settings**
2. 왼쪽 메뉴에서 **Secrets and variables** → **Actions** 클릭
3. **New repository secret** 클릭
4. Name과 Value 입력
5. **Add secret** 클릭

## 확인 방법

### Actions 로그에서 확인:
워크플로우 실행 후 로그에서 다음을 확인:

```
🔍 환경 변수 확인:
  CMC_API_KEY: ✅ 설정됨 (0b6290bfe3...)
  TELEGRAM_BOT_TOKEN: ✅ 설정됨 (8362947773...)
  TELEGRAM_CHAT_ID: 57364261 (type: str)
```

만약 "❌ 없음"이 표시되면 해당 Secret이 설정되지 않은 것입니다.

## 문제 해결

### 문제 1: TELEGRAM_CHAT_ID가 "❌ 없음"으로 표시
**해결**: GitHub Secrets에 `TELEGRAM_CHAT_ID` 추가

### 문제 2: "Chat not found" 오류
**해결**: 
1. 텔레그램에서 봇 찾기: @coinmarketcap1230bot
2. 봇에게 `/start` 메시지 보내기
3. 봇이 응답하는지 확인
4. 그 후 GitHub Actions 다시 실행

### 문제 3: 로그에 "전송 완료"가 있는데 메시지가 안 옴
**확인 사항**:
1. 봇이 차단되지 않았는지 확인
2. 다른 기기에서도 확인
3. 텔레그램 앱을 재시작
4. 봇에게 다시 `/start` 보내기

## 테스트

로컬에서 테스트:
```bash
python test_portfolio_monitor.py
```

로컬에서 성공하면 코드는 정상입니다. GitHub Secrets 설정만 확인하면 됩니다.


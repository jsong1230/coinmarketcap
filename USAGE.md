# CryptoWatcher 사용 가이드

## 빠른 시작

### 1. 환경 설정

CMC API 키는 이미 설정되었습니다. 텔레그램 봇 토큰만 추가하면 됩니다.

#### 텔레그램 봇 토큰 받기:
1. 텔레그램에서 [@BotFather](https://t.me/botfather) 찾기
2. `/newbot` 명령어로 새 봇 생성
3. 받은 토큰을 `.env` 파일의 `TELEGRAM_BOT_TOKEN`에 입력

```bash
# .env 파일 편집
nano .env
# 또는
vim .env
```

### 2. 설치 및 실행

```bash
# 가상환경 생성 (처음 한 번만)
python3.11 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 초기화
alembic upgrade head

# 서버 실행
python run.py
```

또는 자동 설정 스크립트 사용:

```bash
./setup.sh
python run.py
```

### 3. 사용 방법

#### 텔레그램 봇 사용:
1. 텔레그램에서 생성한 봇 찾기
2. `/start` 명령어로 시작
3. `/help` 명령어로 사용 가능한 명령어 확인

#### API 사용:
- API 문서: http://localhost:8000/docs
- Swagger UI에서 직접 테스트 가능

### 4. 주요 기능

#### 텔레그램 명령어:
- `/start` - 봇 시작 및 사용자 등록
- `/summary` - 포트폴리오 요약 조회
- `/alerts` - 현재 알림 설정 조회
- `/set_alert` - 알림 기준 설정
- `/advice` - 투자 조언 요청
- `/help` - 도움말

#### API 엔드포인트:
- `POST /api/users` - 사용자 등록
- `GET /api/users/{telegram_chat_id}` - 사용자 조회
- `POST /api/portfolio` - 포트폴리오 항목 추가
- `GET /api/portfolio/summary` - 포트폴리오 요약
- `GET /api/alerts` - 알림 설정 조회
- `PUT /api/alerts` - 알림 설정 업데이트

### 5. 포트폴리오 설정 예시

#### 텔레그램으로:
1. `/start` 명령어로 등록
2. API를 통해 포트폴리오 추가

#### API로 직접:
```bash
# 사용자 등록
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_chat_id": "123456789",
    "cmc_api_key": "REMOVED_SECRET",
    "base_currency": "USD"
  }'

# 포트폴리오 항목 추가
curl -X POST "http://localhost:8000/api/portfolio?telegram_chat_id=123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC",
    "quantity": 0.5
  }'

# 포트폴리오 요약 조회
curl "http://localhost:8000/api/portfolio/summary?telegram_chat_id=123456789"
```

### 6. 알림 설정

```bash
curl -X PUT "http://localhost:8000/api/alerts?telegram_chat_id=123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "single_coin_percentage_threshold": 5.0,
    "portfolio_percentage_threshold": 10.0,
    "min_notification_interval_minutes": 15
  }'
```

### 7. 문제 해결

#### 텔레그램 봇이 응답하지 않을 때:
- `.env` 파일의 `TELEGRAM_BOT_TOKEN` 확인
- 봇이 실행 중인지 확인
- 로그 확인

#### CMC API 오류:
- API 키가 유효한지 확인
- API 사용량 제한 확인
- 네트워크 연결 확인

#### 데이터베이스 오류:
```bash
# 데이터베이스 재초기화
rm cryptowatcher.db
alembic upgrade head
```


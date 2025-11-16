# 빠른 시작 가이드

## 1. 서버 실행

```bash
cd /Users/joohansong/dev/coinmarketcap
source venv/bin/activate
python run.py
```

또는:

```bash
./start_server.sh
```

## 2. 포트폴리오 등록

### 방법 A: 스크립트 사용 (권장)

```bash
# 텔레그램 chat_id 필요
python register_portfolio.py YOUR_TELEGRAM_CHAT_ID
```

### 방법 B: API 직접 호출

#### 2-1. 사용자 등록
```bash
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_chat_id": "YOUR_TELEGRAM_CHAT_ID",
    "base_currency": "USD"
  }'
```

#### 2-2. 자산 추가
```bash
# BTC
curl -X POST "http://localhost:8000/api/portfolio?telegram_chat_id=YOUR_CHAT_ID" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC", "quantity": 4.4744}'

# ETH
curl -X POST "http://localhost:8000/api/portfolio?telegram_chat_id=YOUR_CHAT_ID" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "ETH", "quantity": 26.52}'

# SOL
curl -X POST "http://localhost:8000/api/portfolio?telegram_chat_id=YOUR_CHAT_ID" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "SOL", "quantity": 100.26}'

# META
curl -X POST "http://localhost:8000/api/portfolio?telegram_chat_id=YOUR_CHAT_ID" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "META", "quantity": 11325.73}'
```

### 방법 C: Swagger UI 사용

1. http://localhost:8000/docs 접속
2. `POST /api/users`로 사용자 등록
3. `POST /api/portfolio`로 각 자산 추가

## 3. 텔레그램 chat_id 확인 방법

1. 텔레그램에서 [@userinfobot](https://t.me/userinfobot)에게 메시지 보내기
2. 또는 봇과 대화 시작 후 확인
3. 숫자로 된 ID를 복사

## 4. 포트폴리오 확인

```bash
curl "http://localhost:8000/api/portfolio/summary?telegram_chat_id=YOUR_CHAT_ID"
```

또는 텔레그램 봇에서:
```
/summary
```

## 5. 알림 설정

```bash
curl -X PUT "http://localhost:8000/api/alerts?telegram_chat_id=YOUR_CHAT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "single_coin_percentage_threshold": 5.0,
    "portfolio_percentage_threshold": 10.0,
    "min_notification_interval_minutes": 15
  }'
```

## 등록할 자산 목록

- **BTC**: 4.4744
- **ETH**: 26.52
- **SOL**: 100.26
- **META**: 11,325.73


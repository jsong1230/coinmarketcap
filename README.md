# CryptoWatcher Bot

CoinMarketCap(CMC) 포트폴리오 데이터를 기반으로 가격 변동을 자동 감지하여 텔레그램으로 실시간 알림을 보내는 자동화 모니터링 서비스입니다.

## 주요 기능

- 📊 CMC API를 통한 실시간 가격 모니터링
- 🔔 텔레그램을 통한 자동 알림
- 💰 포트폴리오 평가액 자동 계산
- ⚙️ 사용자별 알림 기준 설정
- 📈 변동률 분석 및 스냅샷 저장

## 요구사항

- Python 3.11+
- CoinMarketCap API Key
- Telegram Bot Token

## 설치

1. 저장소 클론:
```bash
git clone <repository-url>
cd coinmarketcap
```

2. 가상환경 생성 및 활성화:
```bash
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정:
```bash
cp .env.example .env
# .env 파일을 편집하여 API 키 입력
```

5. 데이터베이스 초기화:
```bash
alembic upgrade head
```

## 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 텔레그램 명령어

- `/start` - 봇 시작 및 초기 설정
- `/summary` - 포트폴리오 요약 조회
- `/alerts` - 현재 알림 설정 조회
- `/set_alert` - 알림 기준 설정
- `/advice` - 투자 조언 요청
- `/help` - 도움말

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 개발

### 테스트 실행
```bash
pytest
```

### 코드 포맷팅
```bash
black .
isort .
```

## 라이선스

MIT


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
pip install --upgrade pip
pip install -r requirements.txt
```

4. 환경 변수 설정:
프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 입력하세요:
```bash
CMC_API_KEY=your_cmc_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=sqlite:///./cryptowatcher.db
HOST=0.0.0.0
PORT=8000
SCHEDULER_INTERVAL_MINUTES=5
```

5. 데이터베이스 초기화:
```bash
alembic upgrade head
```

**참고**: 데이터베이스는 서버 시작 시 자동으로 생성되므로 이 단계는 선택사항입니다.

## 실행

### 서버 실행 (API 서버)

#### 포그라운드 실행 (개발용)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

또는 스크립트 사용:
```bash
chmod +x scripts/start_server.sh  # 처음 한 번만 실행
./scripts/start_server.sh
```

**참고**: 스크립트는 자동으로 프로젝트 루트를 찾고 가상환경을 활성화합니다.

#### 백그라운드 실행 (프로덕션용)

서버를 백그라운드에서 실행하려면:

```bash
chmod +x scripts/start_server_background.sh  # 처음 한 번만 실행
./scripts/start_server_background.sh
```

서버 상태 확인:
```bash
./scripts/status_server.sh
```

서버 종료:
```bash
./scripts/stop_server.sh
```

로그 확인:
```bash
tail -f logs/server.log
```

**참고**: 백그라운드 실행 시 `--reload` 옵션이 비활성화됩니다. 코드 변경 시 서버를 재시작해야 합니다.

### 로컬 모니터링 (백그라운드)

포트폴리오를 자동으로 모니터링하고 텔레그램 알림을 받으려면:

```bash
./scripts/start_monitor.sh
```

상태 확인:
```bash
./scripts/status_monitor.sh
```

중지:
```bash
./scripts/stop_monitor.sh
```

자세한 내용은 [로컬 모니터링 가이드](docs/LOCAL_MONITORING.md)를 참조하세요.

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

## 프로젝트 구조

```
coinmarketcap/
├── app/              # 애플리케이션 코드
├── tests/            # 테스트 코드
├── scripts/          # 유틸리티 스크립트
├── docs/             # 문서
├── alembic/          # 데이터베이스 마이그레이션
└── .github/          # GitHub Actions 워크플로우
```

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

## 문서

자세한 내용은 `docs/` 디렉토리의 문서를 참조하세요:
- [빠른 시작 가이드](docs/QUICK_START.md)
- [사용 방법](docs/USAGE.md)
- [배포 가이드](docs/DEPLOYMENT.md)
- [문제 해결](docs/TROUBLESHOOTING.md)

## 라이선스

MIT


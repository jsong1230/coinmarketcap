# CryptoWatcher Bot

암호화폐 포트폴리오 데이터를 기반으로 가격 변동을 자동 감지하여 텔레그램으로 실시간 알림을 보내는 자동화 모니터링 서비스입니다.

## 주요 기능

- 📊 실시간 가격 모니터링 (CoinMarketCap 또는 CoinGecko API 지원)
- 🔔 텔레그램을 통한 자동 알림
- 💰 포트폴리오 평가액 자동 계산
- ⚙️ 사용자별 알림 기준 설정
- 📈 변동률 분석 및 스냅샷 저장
- 🔄 API 제공자 선택 가능 (CoinMarketCap / CoinGecko)

## 요구사항

- Python 3.11+
- API Key (선택사항):
  - CoinMarketCap API Key (CoinMarketCap 사용 시)
  - CoinGecko API Key (CoinGecko Pro 사용 시, 무료 API는 키 불필요)
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
# 필수 설정
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# API 제공자 선택 (cmc 또는 coingecko)
API_PROVIDER=cmc  # 또는 coingecko

# CoinMarketCap 설정 (API_PROVIDER=cmc일 때)
CMC_API_KEY=your_cmc_api_key_here

# CoinGecko 설정 (API_PROVIDER=coingecko일 때, 선택사항)
COINGECKO_API_KEY=your_coingecko_api_key  # 무료 API 사용 시 생략 가능

# 선택 설정 (자동 설정 기능 사용 시)
TELEGRAM_CHAT_ID=your_telegram_chat_id  # 텔레그램 @userinfobot으로 확인 가능
BASE_CURRENCY=KRW  # 기본 통화 (기본값: KRW)
PORTFOLIO_JSON={"BTC": 4.4744, "ETH": 26.52, "SOL": 100.26}  # 포트폴리오 정보

# 서버 설정
DATABASE_URL=sqlite:///./cryptowatcher.db
HOST=0.0.0.0
PORT=8000
SCHEDULER_INTERVAL_MINUTES=30
```

**API 제공자 선택:**

- **CoinMarketCap (`API_PROVIDER=cmc`)**:
  - `CMC_API_KEY` 필수
  - 주식 심볼 지원 (예: META, AAPL)
  - 유료 API (무료 티어 제한 있음)

- **CoinGecko (`API_PROVIDER=coingecko`)**:
  - `COINGECKO_API_KEY` 선택사항 (무료 공개 API 사용 가능)
  - 무료 API: API 키 없이 사용 가능 (rate limit 있음)
  - Pro API: API 키 필요 (더 높은 rate limit)
  - 주로 암호화폐 지원 (주식 심볼 미지원)

**자동 설정 기능:**
- `TELEGRAM_CHAT_ID`와 API 키를 설정하면 서버 시작 시 자동으로 사용자 정보가 업데이트됩니다.
  - CoinMarketCap 사용 시: `CMC_API_KEY` 설정
  - CoinGecko 사용 시: `COINGECKO_API_KEY` 설정 (선택사항, 무료 API는 생략 가능)
- `API_PROVIDER`를 설정하면 서버 시작 시 자동으로 API 제공자가 업데이트됩니다.
- `PORTFOLIO_JSON`을 설정하면 서버 시작 시 자동으로 포트폴리오가 등록/업데이트됩니다.
- 자산을 변경하려면 `.env`의 `PORTFOLIO_JSON`을 수정하고 서버를 재시작하세요.

5. Git hooks 설치 (선택사항, 권장):

```bash
chmod +x scripts/setup_git_hooks.sh
./scripts/setup_git_hooks.sh
```

**참고**: Git hooks는 커밋 전에 README.md와 CHANGELOG.md 업데이트를 확인합니다.

6. 데이터베이스 초기화:

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

- `/start` - 봇 시작 및 초기 설정 (먼저 실행 필요)
- `/summary` - 포트폴리오 요약 조회
- `/alerts` - 현재 알림 설정 조회
- `/set_portfolio` - 포트폴리오 등록 (.env의 PORTFOLIO_JSON 사용)
- `/set_alert` - 알림 기준 설정 (API 사용)
- `/advice` - 투자 조언 요청
- `/help` - 도움말

## 자산 변경 방법

포트폴리오 자산을 변경하려면:

1. `.env` 파일에서 `PORTFOLIO_JSON` 수정:

   ```bash
   PORTFOLIO_JSON={"BTC": 5.0, "ETH": 30.0, "SOL": 120.0}
   ```

2. 서버 재시작:

   ```bash
   ./scripts/stop_server.sh
   ./scripts/start_server_background.sh
   ```

서버 재시작 시 기존 포트폴리오가 자동으로 삭제되고 `.env`의 새 값으로 등록됩니다.

**참고**: CoinGecko를 사용하는 경우 주식 심볼(예: META, AAPL)은 지원하지 않습니다. 주식 심볼이 포함된 포트폴리오는 CoinMarketCap을 사용하세요.

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## 프로젝트 구조

```text
coinmarketcap/
├── app/                    # 애플리케이션 코드
│   ├── cmc_client.py      # CoinMarketCap API 클라이언트
│   ├── coingecko_client.py # CoinGecko API 클라이언트
│   ├── main.py            # FastAPI 애플리케이션
│   ├── models.py          # 데이터베이스 모델
│   ├── services.py         # 비즈니스 로직
│   ├── scheduler.py        # 스케줄러 (가격 모니터링)
│   └── telegram_bot.py     # 텔레그램 봇
├── tests/                  # 테스트 코드
├── scripts/                # 유틸리티 스크립트
├── docs/                   # 문서
├── alembic/                # 데이터베이스 마이그레이션
└── .github/                # GitHub Actions 워크플로우
```

## 개발

### Git Hooks

커밋 전에 README.md와 CHANGELOG.md 업데이트를 확인하는 pre-commit hook이 포함되어 있습니다.

설치:

```bash
./scripts/setup_git_hooks.sh
```

**주의**: 코드를 변경할 때는 항상 README.md와 CHANGELOG.md를 함께 업데이트하세요.

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

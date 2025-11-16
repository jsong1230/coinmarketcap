# 로컬 모니터링 가이드

로컬 컴퓨터에서 백그라운드로 포트폴리오 모니터링을 실행하는 방법입니다.

## 사전 준비

### 1. 환경 변수 설정

`.env` 파일에 다음 환경 변수를 설정하세요:

```bash
CMC_API_KEY=your_cmc_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
BASE_CURRENCY=KRW
MONITOR_INTERVAL_HOURS=1
PORTFOLIO_JSON='{"BTC": 4.4744, "ETH": 26.52, "SOL": 100.26, "META": 11325.73}'
```

또는 환경 변수로 직접 설정:

```bash
export CMC_API_KEY="your_cmc_api_key"
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
export TELEGRAM_CHAT_ID="your_telegram_chat_id"
export BASE_CURRENCY="KRW"
export MONITOR_INTERVAL_HOURS=1
export PORTFOLIO_JSON='{"BTC": 4.4744, "ETH": 26.52, "SOL": 100.26, "META": 11325.73}'
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

## 사용 방법

### 모니터링 시작

```bash
./scripts/start_monitor.sh
```

또는 직접 실행:

```bash
python scripts/local_monitor.py
```

### 모니터링 상태 확인

```bash
./scripts/status_monitor.sh
```

또는 로그 파일 확인:

```bash
tail -f logs/monitor.log
```

### 모니터링 중지

```bash
./scripts/stop_monitor.sh
```

또는 PID 파일을 통해 직접 종료:

```bash
kill $(cat monitor.pid)
```

## 백그라운드 실행

`start_monitor.sh` 스크립트는 자동으로 백그라운드에서 실행됩니다. 터미널을 닫아도 계속 실행됩니다.

## 로그 파일

- **모니터링 로그**: `logs/monitor.log`
- **시작 로그**: `logs/monitor_startup.log`

## 설정 옵션

### 실행 간격 변경

기본값은 1시간입니다. 변경하려면:

```bash
export MONITOR_INTERVAL_HOURS=2  # 2시간마다 실행
./scripts/start_monitor.sh
```

### 포트폴리오 변경

`.env` 파일 또는 환경 변수에서 `PORTFOLIO_JSON`을 수정한 후 모니터링을 재시작하세요.

## 문제 해결

### 이미 실행 중이라는 오류

```bash
./scripts/stop_monitor.sh  # 먼저 종료
./scripts/start_monitor.sh  # 다시 시작
```

### 프로세스가 보이지 않지만 PID 파일이 있는 경우

```bash
rm monitor.pid  # PID 파일 삭제
./scripts/start_monitor.sh  # 다시 시작
```

### 로그 확인

```bash
# 실시간 로그 확인
tail -f logs/monitor.log

# 최근 50줄 확인
tail -n 50 logs/monitor.log

# 오류만 확인
grep ERROR logs/monitor.log
```

## 자동 시작 설정 (선택사항)

### macOS (launchd)

`~/Library/LaunchAgents/com.cryptowatcher.monitor.plist` 파일 생성:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cryptowatcher.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/your_username/dev/coinmarketcap/scripts/start_monitor.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/your_username/dev/coinmarketcap</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/your_username/dev/coinmarketcap/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/your_username/dev/coinmarketcap/logs/launchd.error.log</string>
</dict>
</plist>
```

로드:

```bash
launchctl load ~/Library/LaunchAgents/com.cryptowatcher.monitor.plist
```

### Linux (systemd)

`/etc/systemd/system/cryptowatcher-monitor.service` 파일 생성:

```ini
[Unit]
Description=CryptoWatcher Portfolio Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/coinmarketcap
Environment="PATH=/path/to/coinmarketcap/venv/bin"
ExecStart=/path/to/coinmarketcap/venv/bin/python /path/to/coinmarketcap/scripts/local_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

활성화:

```bash
sudo systemctl enable cryptowatcher-monitor
sudo systemctl start cryptowatcher-monitor
```

## 장점

✅ **로컬 제어**: 완전한 제어권
✅ **빠른 응답**: 네트워크 지연 최소화
✅ **무료**: 서버 비용 없음
✅ **데이터 보안**: 로컬에서만 실행

## 주의사항

⚠️ **컴퓨터가 켜져 있어야 함**: 백그라운드 실행이지만 컴퓨터가 꺼지면 중지됩니다.
⚠️ **인터넷 연결 필요**: CMC API와 텔레그램 API 접근 필요
⚠️ **전력 소비**: 지속적인 실행으로 인한 전력 소비


# 문제 해결 가이드

## 서버 실행 문제

### 문제 1: "ModuleNotFoundError: No module named 'telegram'"
**원인**: 가상환경이 활성화되지 않았거나 의존성이 설치되지 않음

**해결**:
```bash
# 가상환경 생성 (없는 경우)
python3.11 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
```

### 문제 2: "There is no current event loop in thread"
**원인**: 텔레그램 봇이 별도 스레드에서 실행될 때 이벤트 루프가 없음

**해결**: 최신 버전의 코드를 사용하면 자동으로 해결됩니다. 코드를 최신으로 업데이트하세요.

### 문제 3: 스크립트 실행 권한 오류
**원인**: 스크립트에 실행 권한이 없음

**해결**:
```bash
chmod +x scripts/start_server.sh
```

### 문제 4: ".env 파일을 찾을 수 없음"
**원인**: 환경 변수 파일이 없음

**해결**: 프로젝트 루트에 `.env` 파일을 생성하고 필요한 환경 변수를 설정하세요:
```bash
CMC_API_KEY=your_cmc_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=sqlite:///./cryptowatcher.db
HOST=0.0.0.0
PORT=8000
SCHEDULER_INTERVAL_MINUTES=5
```

## 텔레그램 메시지가 오지 않는 경우

### 1. GitHub Actions 로그 확인

Actions 탭 → 워크플로우 실행 → 로그에서 다음을 확인:

#### ✅ 정상적인 경우:
```
✅ 텔레그램 메시지 전송 완료!
   메시지 ID: 12345
   채팅 ID: 57364261
```

#### ❌ 문제가 있는 경우:
- "❌ 텔레그램 전송 실패" 메시지 확인
- 오류 메시지 확인

### 2. 일반적인 문제들

#### 문제 1: "Chat not found" 오류
**원인**: Chat ID가 잘못되었거나 봇이 해당 채팅에 접근할 수 없음

**해결**:
1. 봇에게 먼저 메시지를 보내야 합니다
2. 텔레그램에서 봇 찾기: @coinmarketcap1230bot
3. `/start` 명령어 보내기
4. 그 후 GitHub Actions 실행

#### 문제 2: "Unauthorized" 오류
**원인**: 봇 토큰이 잘못되었음

**해결**:
1. GitHub Secrets에서 `TELEGRAM_BOT_TOKEN` 확인
2. @BotFather에서 토큰 재확인

#### 문제 3: 로그에 "전송 완료"가 있는데 메시지가 안 옴
**원인**: 
- Chat ID가 문자열로 전달되어 전송 실패했을 수 있음
- 봇이 차단되었을 수 있음

**해결**:
1. 봇이 차단되지 않았는지 확인
2. 봇에게 `/start` 명령어 다시 보내기
3. GitHub Secrets에서 `TELEGRAM_CHAT_ID`가 숫자로만 되어 있는지 확인 (예: `57364261`)

### 3. 테스트 방법

#### 로컬에서 테스트:
```bash
# 프로젝트 루트로 이동
cd /path/to/coinmarketcap

# 가상환경 활성화
source venv/bin/activate  # Windows: venv\Scripts\activate

# 테스트 실행
python scripts/test_portfolio_monitor.py
```

#### GitHub Actions에서 테스트:
1. Actions 탭 → "Portfolio Monitor"
2. "Run workflow" 클릭
3. 로그 확인

### 4. 확인 체크리스트

- [ ] GitHub Secrets에 `TELEGRAM_CHAT_ID` 설정됨 (숫자만, 예: `57364261`)
- [ ] GitHub Secrets에 `TELEGRAM_BOT_TOKEN` 설정됨
- [ ] GitHub Secrets에 `CMC_API_KEY` 설정됨
- [ ] 텔레그램에서 봇에게 `/start` 명령어 보냄
- [ ] 봇이 차단되지 않음
- [ ] Actions 로그에서 오류 메시지 확인

### 5. 디버깅 팁

로그에서 다음 정보를 확인하세요:
- 환경 변수 확인 로그
- 봇 정보 확인 로그
- 채팅 정보 확인 로그
- 메시지 전송 결과

모든 로그가 정상인데도 메시지가 안 오면:
1. 봇에게 직접 메시지 보내기 테스트
2. Chat ID 재확인
3. 봇 토큰 재확인


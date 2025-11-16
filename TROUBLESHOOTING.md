# 문제 해결 가이드

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
cd /Users/joohansong/dev/coinmarketcap
source venv/bin/activate
python test_portfolio_monitor.py
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


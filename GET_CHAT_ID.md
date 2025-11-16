# 텔레그램 Chat ID 확인 방법

## 방법 1: @userinfobot 사용 (가장 간단)

1. 텔레그램에서 [@userinfobot](https://t.me/userinfobot) 검색
2. 봇에게 아무 메시지나 보내기
3. 봇이 응답으로 **ID**를 알려줍니다
   - 예: `Id: 57364261`

## 방법 2: 봇과 대화 후 스크립트 실행

1. 텔레그램에서 생성한 봇 찾기
2. 봇에게 메시지 보내기 (예: `/start` 또는 아무 메시지)
3. 로컬에서 스크립트 실행:

```bash
cd /Users/joohansong/dev/coinmarketcap
source venv/bin/activate
export TELEGRAM_BOT_TOKEN="your_bot_token"
python get_telegram_chat_id.py
```

## 방법 3: 봇 코드로 확인

봇에게 메시지를 보내면 자동으로 chat_id를 알려주는 기능 추가:

```python
# 봇 코드에 추가
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"당신의 Chat ID는: {chat_id}입니다.")
```

## 방법 4: 웹 브라우저로 확인

1. 브라우저에서 다음 URL 열기:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
2. 봇에게 메시지를 보낸 후 페이지 새로고침
3. JSON 응답에서 `"chat":{"id":숫자}` 찾기

## 현재 설정된 Chat ID

이전에 확인한 Chat ID: `57364261`

하지만 다시 확인하려면 위의 방법 중 하나를 사용하세요.

## GitHub Secrets에 설정

확인한 Chat ID를 GitHub Secrets에 추가:

1. 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭
3. Name: `TELEGRAM_CHAT_ID`
4. Value: 확인한 Chat ID (예: `57364261`)


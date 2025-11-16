# 배포 가이드

## 현재 상태
현재는 **로컬 환경**에서 서버가 실행되고 있습니다. 24시간 운영하려면 클라우드 서버에 배포해야 합니다.

## 배포 옵션

### 1. 클라우드 서버 (VPS)
- **추천**: AWS EC2, DigitalOcean, Linode, Vultr 등
- 장점: 완전한 제어, 저렴한 비용
- 단점: 서버 관리 필요

### 2. PaaS (Platform as a Service)
- **Heroku**: 간단한 배포, 무료 티어 있음
- **Railway**: GitHub 연동, 자동 배포
- **Render**: 무료 티어, 쉬운 설정
- 장점: 관리 편리, 자동 스케일링
- 단점: 무료 티어 제한

### 3. Docker + 클라우드
- Docker 컨테이너로 패키징
- 어디서든 실행 가능

## 빠른 배포: Railway (추천)

### 1. Railway 계정 생성
- https://railway.app 접속
- GitHub 계정으로 로그인

### 2. 프로젝트 연결
- "New Project" → "Deploy from GitHub repo"
- `coinmarketcap` 저장소 선택

### 3. 환경 변수 설정
Railway 대시보드에서 다음 환경 변수 추가:
```
CMC_API_KEY=your_cmc_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=postgresql://... (Railway가 자동 생성)
HOST=0.0.0.0
PORT=$PORT
SCHEDULER_INTERVAL_MINUTES=5
```

### 4. 자동 배포
- GitHub에 push하면 자동 배포
- 24시간 실행 보장

## 빠른 배포: Render

### 1. Render 계정 생성
- https://render.com 접속
- GitHub 계정으로 로그인

### 2. 새 Web Service 생성
- "New" → "Web Service"
- GitHub 저장소 연결
- 설정:
  - Build Command: `pip install -r requirements.txt && alembic upgrade head`
  - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. 환경 변수 설정
Render 대시보드에서 환경 변수 추가 (위와 동일)

## 로컬에서 계속 실행하기

현재 로컬에서 실행 중이라면:

### 백그라운드 실행
```bash
cd /Users/joohansong/dev/coinmarketcap
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &
```

### 상태 확인
```bash
# 로그 확인
tail -f server.log

# 프로세스 확인
ps aux | grep uvicorn

# 서버 중지
pkill -f "uvicorn app.main:app"
```

### 문제점
- 컴퓨터를 끄면 서버도 종료됨
- 네트워크 문제 시 접근 불가
- 24시간 운영 어려움

## 추천: Railway 또는 Render
- 무료 티어 제공
- GitHub 연동으로 자동 배포
- 24시간 실행 보장
- 간단한 설정

원하는 배포 방법을 알려주시면 상세 가이드를 제공하겠습니다!


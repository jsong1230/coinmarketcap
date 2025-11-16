# 스크립트 목록

이 디렉토리에는 유틸리티 스크립트들이 있습니다.

## 포트폴리오 관련

- **check_portfolio.py** - 포트폴리오 확인 스크립트
- **register_portfolio.py** - 포트폴리오 등록 스크립트
- **test_portfolio_monitor.py** - 포트폴리오 모니터링 테스트 스크립트

## 텔레그램 관련

- **get_telegram_chat_id.py** - 텔레그램 Chat ID 확인 스크립트

## 서버 관리

- **setup.sh** - 프로젝트 설정 스크립트
- **start_server.sh** - 서버 시작 스크립트
- **remove_secrets.sh** - Git 히스토리에서 Secret 제거 스크립트

## 사용 방법

각 스크립트는 독립적으로 실행할 수 있습니다:

```bash
# 가상환경 활성화
source venv/bin/activate

# 스크립트 실행
python scripts/check_portfolio.py
python scripts/get_telegram_chat_id.py
```


# Changelog

모든 주요 변경사항은 이 파일에 기록됩니다.

## [Unreleased]

### Added
- `/set_portfolio` 텔레그램 봇 명령어 추가 (.env의 PORTFOLIO_JSON 사용)
- Git pre-commit hook 추가 (커밋 전 README.md, CHANGELOG.md 업데이트 확인)
- CHANGELOG.md 파일 추가
- Git hooks 설치 스크립트 (scripts/setup_git_hooks.sh)

### Changed
- 요약 메시지 전송 주기를 1시간에서 3시간으로 변경
- 기본 통화를 USD에서 KRW로 변경

### Added (이전)
- .env 기반 자동 설정 기능 (TELEGRAM_CHAT_ID, BASE_CURRENCY, PORTFOLIO_JSON)
- 포트폴리오 자동 업데이트 기능
- 백그라운드 서버 실행 스크립트 (start_server_background.sh, stop_server.sh, status_server.sh)
- 스케줄러 상세 로깅 추가

### Fixed (이전)
- 텔레그램 봇 이벤트 루프 및 시그널 핸들러 오류 수정
- 텔레그램 봇 충돌 오류 처리 개선
- start_command에서 db.flush() 추가로 사용자 등록 오류 수정
- UserUpdate 스키마 추가로 API 업데이트 오류 수정


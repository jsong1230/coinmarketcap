# GitHub Actions 워크플로우 설정

## 현재 상황
코드는 성공적으로 푸시되었지만, GitHub Actions 워크플로우 파일(`.github/workflows/ci.yml`)을 푸시하는 데 권한 문제가 발생했습니다.

## 해결 방법

### 방법 1: GitHub 웹 인터페이스에서 직접 추가 (권장)

1. GitHub 저장소로 이동: https://github.com/jsong1230/coinmarketcap
2. **Add file** → **Create new file** 클릭
3. 파일 경로 입력: `.github/workflows/ci.yml`
4. 아래 내용을 복사하여 붙여넣기:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip packages
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --tb=short
      env:
        CMC_API_KEY: ${{ secrets.CMC_API_KEY }}
        TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        DATABASE_URL: sqlite:///./test.db
    
    - name: Check code formatting
      run: |
        pip install black
        black --check app/ tests/ || true
```

5. **Commit new file** 클릭

### 방법 2: GitHub CLI 토큰 권한 업데이트

```bash
# GitHub CLI 재인증 (workflow 스코프 포함)
gh auth refresh -s workflow

# 워크플로우 파일 푸시
git push origin main
```

### 방법 3: Personal Access Token 사용

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 새 토큰 생성 (workflow 스코프 포함)
3. 로컬에서 토큰으로 인증:

```bash
git remote set-url origin https://토큰@github.com/jsong1230/coinmarketcap.git
git push origin main
```

## GitHub Secrets 설정

워크플로우가 작동하려면 Secrets를 설정해야 합니다:

1. 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭
3. 다음 Secrets 추가:
   - `CMC_API_KEY`: `REMOVED_SECRET`
   - `TELEGRAM_BOT_TOKEN`: `REMOVED_SECRET`

## 확인

워크플로우 파일 추가 후:
1. **Actions** 탭에서 워크플로우 실행 확인
2. Secrets 설정 후 테스트가 정상 실행되는지 확인


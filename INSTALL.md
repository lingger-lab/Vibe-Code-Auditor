# 설치 가이드

## 사전 요구사항

### 1. Python 3.12 이상
```bash
# Python 버전 확인
python --version
```

### 2. pip 최신 버전
```bash
# pip 업그레이드
python -m pip install --upgrade pip
```

## 설치 단계

### 방법 1: 개발 모드 설치 (권장)

```bash
# 1. 프로젝트 디렉토리로 이동
cd "C:\Users\USER\Desktop\Vibe-Code Auditor"

# 2. 가상 환경 생성 (선택사항이지만 권장)
python -m venv venv

# 3. 가상 환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. 의존성 설치
pip install -r requirements.txt

# 5. 개발 모드로 설치
pip install -e .
```

### 방법 2: 직접 실행

```bash
# 1. 의존성만 설치
pip install -r requirements.txt

# 2. Python 모듈로 직접 실행
python -m src.cli.main --help
```

## API 키 설정

### 1. .env 파일 생성
```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env
```

### 2. Anthropic API 키 입력
`.env` 파일을 편집하여 다음과 같이 입력:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxx
```

API 키 발급:
1. [Anthropic Console](https://console.anthropic.com/) 방문
2. 계정 생성 또는 로그인
3. API Keys 섹션에서 새 키 생성
4. 생성된 키를 복사하여 .env 파일에 붙여넣기

## 선택적 도구 설치

### ESLint (JavaScript/TypeScript 분석용)
```bash
npm install -g eslint
```

### jscpd (코드 중복 감지용)
```bash
npm install -g jscpd
```

## 설치 확인

### 1. 버전 확인
```bash
vibe-auditor --help
```

또는

```bash
python -m src.cli.main --help
```

### 2. 테스트 실행
```bash
# 유닛 테스트 실행
python -m unittest discover tests

# 특정 테스트 실행
python -m unittest tests.test_language_detector
```

## 문제 해결

### ModuleNotFoundError
```bash
# 현재 디렉토리를 Python 경로에 추가
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Mac/Linux
set PYTHONPATH=%PYTHONPATH%;%cd%         # Windows
```

### API 키 오류
- `.env` 파일이 프로젝트 루트에 있는지 확인
- API 키가 올바르게 입력되었는지 확인
- API 키 앞뒤 공백이 없는지 확인

### 정적 분석 도구 오류
- 각 도구가 올바르게 설치되었는지 확인:
  ```bash
  pylint --version
  semgrep --version
  eslint --version  # Node.js 설치 필요
  jscpd --version   # Node.js 설치 필요
  ```

## 업데이트

```bash
# 최신 의존성으로 업데이트
pip install --upgrade -r requirements.txt

# 개발 모드로 재설치
pip install -e . --force-reinstall
```

## 제거

```bash
# pip로 설치한 경우
pip uninstall vibe-code-auditor

# 가상 환경 삭제 (필요시)
deactivate  # 가상 환경 비활성화
rm -rf venv  # 가상 환경 폴더 삭제
```

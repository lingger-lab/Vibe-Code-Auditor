# Streamlit Cloud 배포 가이드

## 📋 사전 준비

1. **GitHub 저장소 준비**
   - 코드가 이미 GitHub에 푸시되어 있어야 합니다
   - 현재 저장소: `https://github.com/lingger-lab/Vibe-Code-Auditor`

2. **Streamlit Cloud 계정 생성**
   - https://streamlit.io/cloud 에서 GitHub 계정으로 로그인

## 🚀 배포 단계

### 1단계: Streamlit Cloud 접속

1. https://streamlit.io/cloud 접속
2. "Sign up" 또는 "Log in" 클릭
3. GitHub 계정으로 인증

### 2단계: 새 앱 배포

1. "New app" 버튼 클릭
2. 다음 정보 입력:
   - **Repository**: `lingger-lab/Vibe-Code-Auditor`
   - **Branch**: `master`
   - **Main file path**: `src/ui/app.py`
   - **App URL**: 자동 생성 (예: `vibe-code-auditor.streamlit.app`)

### 3단계: 환경 변수 설정

1. "Advanced settings" 클릭
2. "Secrets" 섹션에서 환경 변수 추가:
   ```toml
   ANTHROPIC_API_KEY = "your_api_key_here"
   ```
   
   **중요**: TOML 형식이므로 다음 규칙을 지켜주세요:
   - 키와 값 사이에 `=` 양쪽에 공백 필요
   - 값은 반드시 **따옴표로 감싸야 함** (`"..."` 또는 `'...'`)
   - 여러 환경 변수가 있으면 각각 별도 줄에 작성

### 4단계: 배포 실행

1. "Deploy!" 버튼 클릭
2. 배포 완료까지 2-3분 소요
3. 생성된 URL로 접속하여 앱 확인

## ⚙️ 추가 설정

### requirements.txt 확인

Streamlit Cloud는 자동으로 `requirements.txt`를 인식하여 의존성을 설치합니다.
현재 프로젝트의 `requirements.txt`가 올바르게 설정되어 있는지 확인하세요.

### 포트 설정

Streamlit Cloud는 자동으로 포트를 관리하므로, 코드에서 포트를 명시적으로 설정할 필요가 없습니다.

## 🔒 보안 주의사항

- **API 키**: 반드시 Streamlit Cloud의 "Secrets" 기능을 사용하세요
- **환경 변수**: `.env` 파일은 Git에 커밋하지 마세요 (이미 `.gitignore`에 포함됨)

## 📝 문제 해결

### 배포 실패 시

1. **로그 확인**: Streamlit Cloud 대시보드에서 "Logs" 탭 확인
   - 오류 메시지의 전체 내용을 확인하세요
   - 특히 import 오류, 경로 오류, 파일 접근 오류를 확인하세요

2. **의존성 오류**: `requirements.txt`에 모든 패키지가 포함되어 있는지 확인
   - 빌드 도구(pyinstaller)는 제외해도 됩니다
   - 테스트 도구(pytest)도 선택적으로 제외 가능

3. **경로 오류**: `Main file path`가 올바른지 확인 (`src/ui/app.py`)

4. **환경 변수 오류**: Secrets에 API 키가 올바르게 설정되었는지 확인
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-xxx..."
   ```

5. **플랫폼 호환성 오류**: 
   - Windows 전용 경로가 코드에 없는지 확인
   - PDF 폰트 경로는 자동으로 플랫폼별로 처리됩니다 (v1.10.0+)

### 일반적인 오류와 해결 방법

#### "Error running app"
- **원인**: 코드 실행 중 오류 발생
- **해결**: 
  1. Streamlit Cloud 로그에서 전체 오류 메시지 확인
  2. 로컬에서 동일한 오류가 발생하는지 테스트
  3. import 경로 문제인지 확인

#### "Failed to load resource: ERR_BLOCKED_BY_CLIENT"
- **원인**: 브라우저 확장 프로그램(광고 차단기 등)이 리소스를 차단
- **해결**: 
  1. 브라우저 확장 프로그램 비활성화 후 재시도
  2. 실제 오류는 Streamlit Cloud 로그에서 확인

#### "ModuleNotFoundError"
- **원인**: 필요한 패키지가 `requirements.txt`에 없음
- **해결**: 누락된 패키지를 `requirements.txt`에 추가

#### "PermissionError" 또는 파일 접근 오류
- **원인**: 파일 시스템 접근 권한 문제
- **해결**: Streamlit Cloud는 읽기 전용 파일 시스템을 사용하므로, 파일 쓰기는 임시 디렉토리만 사용 가능

### 로컬 테스트

배포 전 로컬에서 테스트:
```bash
streamlit run src/ui/app.py
```

로컬에서 정상 작동하면 Streamlit Cloud에서도 대부분 정상 작동합니다.

## 🔗 참고 자료

- [Streamlit Cloud 문서](https://docs.streamlit.io/streamlit-cloud)
- [Streamlit 배포 가이드](https://docs.streamlit.io/deploy)


# 🔧 Vibe-Code Auditor 문제 해결 가이드

## UI 모드 문제

### 문제 1: 브라우저가 열렸다가 바로 닫힘

**증상:**
- VibeAuditor.exe 실행 → UI 모드 선택
- 브라우저가 잠깐 열렸다가 즉시 닫힘
- 또는 "Error: exit status 4294967295" 오류

**원인:**
- PyInstaller 실행 파일 환경에서 Streamlit subprocess 실행 문제
- Streamlit 정적 파일 경로 문제

**해결 방법 (v1.9.0 이후 적용됨):**

1. **최신 버전 사용** (v1.9.0+)
   - Streamlit을 직접 임베드하여 실행
   - subprocess 대신 `streamlit.web.cli` 직접 호출

2. **대안: Python 소스코드로 실행**
   ```bash
   # 방법 1: run_ui.py 사용
   python run_ui.py

   # 방법 2: Streamlit 직접 실행
   python -m streamlit run src/ui/app.py
   ```

3. **대안: CLI 모드 사용**
   ```bash
   # VibeAuditor.exe 실행 후 1번 선택
   # 또는
   python -m src.cli.main --path ./project --mode deployment
   ```

### 문제 2: "Module not found" 오류

**증상:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**해결 방법:**
```bash
pip install -r requirements.txt
```

### 문제 3: 잘못된 포트 사용 (Port 3000 instead of 8501)

**증상:**
- Streamlit이 포트 3000에서 실행됨
- http://localhost:3000 에 연결 불가
- 기대: http://localhost:8501

**원인:**
- Streamlit 기본 설정 부재
- PyInstaller 빌드 시 config.toml 미포함

**해결 방법 (v1.9.0+ 적용됨):**

1. **최신 버전 사용** (v1.9.0+)
   - `.streamlit/config.toml` 파일 포함
   - 포트 8501로 고정 설정

2. **수동 확인**
   ```bash
   # .streamlit/config.toml 존재 확인
   cat .streamlit/config.toml

   # 내용:
   [server]
   port = 8501
   headless = true

   [global]
   developmentMode = false
   ```

### 문제 4: 포트 충돌 (Port 8501 already in use)

**증상:**
```
OSError: [Errno 98] Address already in use
```

**해결 방법:**

**Windows:**
```bash
# 8501 포트 사용 중인 프로세스 확인
netstat -ano | findstr :8501

# 프로세스 종료 (PID 확인 후)
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# 8501 포트 사용 중인 프로세스 확인
lsof -i :8501

# 프로세스 종료
kill -9 <PID>
```

---

## CLI 모드 문제

### 문제 1: API 키 오류

**증상:**
```
AuthenticationError: Invalid API key
```

**해결 방법:**
1. `.env` 파일 생성
   ```bash
   cp .env.example .env
   ```

2. API 키 입력
   ```bash
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

3. API 키 발급
   - https://console.anthropic.com/ 방문
   - API Keys 탭에서 새 키 생성

### 문제 2: 경로 오류

**증상:**
```
Error: Path does not exist
```

**해결 방법:**
- 절대 경로 사용
- Windows: `C:\Users\YourName\project`
- Linux/Mac: `/home/username/project`

---

## 빌드 문제

### 문제 1: 실행 파일이 너무 큼 (3GB+)

**원인:**
- TensorFlow, PyTorch 등 ML 라이브러리 포함

**해결 방법:**
- `VibeAuditor.spec` 파일에서 불필요한 라이브러리 제외

```python
excludes=[
    'tensorflow', 'torch', 'sklearn',
    'scipy.linalg', 'scipy.stats',
    'sympy', 'numba'
]
```

- 다시 빌드:
```bash
pyinstaller VibeAuditor.spec
```

**결과:** 3.1GB → 140MB (95.5% 감소)

### 문제 2: 빌드 실패

**증상:**
```
ImportError during analysis
```

**해결 방법:**
1. 모든 의존성 설치 확인
   ```bash
   pip install -r requirements.txt
   ```

2. PyInstaller 업데이트
   ```bash
   pip install --upgrade pyinstaller
   ```

3. 캐시 정리 후 재빌드
   ```bash
   rm -rf build dist
   pyinstaller VibeAuditor.spec
   ```

---

## 성능 문제

### 문제 1: 분석이 너무 느림

**해결 방법:**

1. **캐시 활성화**
   - UI: "캐시 사용" 체크박스 활성화
   - CLI: 기본적으로 캐시 사용

2. **AI 분석 건너뛰기**
   - UI: "AI 분석 건너뛰기" 체크
   - CLI: `--skip-ai` 플래그 사용
   ```bash
   python -m src.cli.main --path ./project --mode deployment --skip-ai
   ```

3. **대용량 프로젝트**
   - node_modules, .venv 등 제외
   - `.vibe-auditor.yml` 설정 파일 사용

### 문제 2: 메모리 부족

**증상:**
```
MemoryError
```

**해결 방법:**
1. 작은 단위로 분석 (디렉토리별)
2. 불필요한 파일 제외
3. 시스템 RAM 확인 (최소 2GB 권장)

---

## 권한 문제

### 문제 1: Permission Denied

**증상:**
```
PermissionError: [Errno 13] Permission denied
```

**해결 방법:**

**Windows:**
```bash
# 관리자 권한으로 실행
우클릭 → "관리자 권한으로 실행"
```

**Linux/Mac:**
```bash
# 실행 권한 부여
chmod +x VibeAuditor
```

---

## 네트워크 문제

### 문제 1: API 연결 실패

**증상:**
```
ConnectionError: Unable to connect to API
```

**해결 방법:**
1. 인터넷 연결 확인
2. 방화벽 설정 확인
3. 프록시 환경인 경우 환경 변수 설정
   ```bash
   export HTTP_PROXY=http://proxy:port
   export HTTPS_PROXY=https://proxy:port
   ```

---

## 기타 문제

### 문제 1: 한글 경로 문제

**증상:**
- 한글이 포함된 경로에서 오류 발생

**해결 방법:**
- 영문 경로 사용 권장
- 또는 절대 경로로 지정

### 문제 2: 로그 확인

**위치:**
- Windows: `%TEMP%\vibe-auditor\logs`
- Linux/Mac: `/tmp/vibe-auditor/logs`

**확인 방법:**
```bash
# 최근 로그 확인
tail -f /tmp/vibe-auditor/logs/app.log
```

---

## 🆘 추가 지원

### 문제가 해결되지 않는 경우

1. **GitHub Issues**
   - https://github.com/lingger-lab/Vibe-Code-Auditor/issues
   - 버그 리포트 또는 질문 게시

2. **정보 포함하기**
   ```
   - OS 버전 (Windows 10/11, Ubuntu 20.04 등)
   - Python 버전 (python --version)
   - 오류 메시지 전체
   - 실행 명령어
   - 스크린샷 (선택사항)
   ```

3. **로그 첨부**
   - 오류 발생 시 로그 파일 첨부

---

## 버전별 알려진 문제

### v1.9.0
- ✅ **수정됨**: UI 모드 브라우저 즉시 닫힘 문제
  - Streamlit 직접 임베드 방식으로 수정

- ✅ **수정됨**: 실행 파일 크기 문제
  - ML 라이브러리 제외 (3.1GB → 140MB)

- ✅ **수정됨**: 잘못된 포트 사용 (3000 대신 8501)
  - .streamlit/config.toml 추가로 포트 고정

- ✅ **수정됨**: PackageNotFoundError
  - PyInstaller spec에 metadata 수집 추가

- ✅ **수정됨**: 포트 설정 충돌 (developmentMode)
  - 수동 포트 지정 제거, config 파일로 관리

### v1.8.0
- ⚠️ **알려진 문제**: 대량 이슈 렌더링 느림
  - v1.8.0에서 페이지네이션으로 해결

---

**최종 업데이트**: 2025-12-02
**버전**: 1.9.0

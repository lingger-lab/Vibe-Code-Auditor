# 📝 로깅 가이드

## 로그 레벨 설명

Vibe-Code Auditor는 3가지 로그 레벨을 제공합니다:

### 1. 기본 모드 (WARNING 레벨)

```powershell
python -m src.cli.main --path examples/sample-project --mode deployment
```

**출력되는 로그:**
- ⚠️ WARNING: 중요한 경고 (타임아웃, 도구 미설치 등)
- ❌ ERROR: 에러 발생
- 🔴 CRITICAL: 치명적 오류

**출력되지 않는 로그:**
- INFO: 일반 정보
- DEBUG: 디버깅 정보

**사용 시나리오:**
- 일반적인 프로젝트 분석
- 깔끔한 출력 선호
- 중요한 문제만 확인

---

### 2. Verbose 모드 (DEBUG 레벨) - 권장

```powershell
python -m src.cli.main --path examples/sample-project --mode deployment --verbose
# 또는 짧게
python -m src.cli.main --path examples/sample-project --mode deployment -v
```

**출력되는 로그:**
- 🐛 DEBUG: 모든 세부 정보
- ℹ️ INFO: 진행 상황
- ⚠️ WARNING: 경고
- ❌ ERROR: 에러
- 🔴 CRITICAL: 치명적 오류

**사용 시나리오:**
- 문제 디버깅
- 분석 과정 상세히 확인
- 성능 모니터링
- 개발 중

**예상 출력:**
```
🔍 Vibe-Code Auditor v1.1

[09:04:39] DEBUG    Verbose mode enabled
[09:04:39] DEBUG    Checking API key...
           INFO     API key found
           DEBUG    Starting language detection
           INFO     Scanning project directory
           DEBUG    Found 1 Python files
           DEBUG    Excluded 0 directories
           INFO     Language detection complete
✓ 감지된 언어: python

[09:04:40] DEBUG    Initializing static analyzer
           INFO     Running Pylint on examples\sample-project
           DEBUG    Pylint command: ['pylint', 'examples\\sample-project', '--output-format=json']
           DEBUG    Pylint timeout: 300s
[09:04:42] DEBUG    Pylint completed in 2.3s
           INFO     Pylint found 5 issues
           DEBUG    Parsing Pylint output
           INFO     Static analysis complete
```

---

### 3. Quiet 모드 (ERROR 레벨)

```powershell
python -m src.cli.main --path examples/sample-project --mode deployment --quiet
# 또는 짧게
python -m src.cli.main --path examples/sample-project --mode deployment -q
```

**출력되는 로그:**
- ❌ ERROR: 에러만 표시
- 🔴 CRITICAL: 치명적 오류

**출력되지 않는 로그:**
- DEBUG, INFO, WARNING 모두 숨김

**사용 시나리오:**
- CI/CD 파이프라인
- 자동화 스크립트
- 에러만 확인

**예상 출력:**
```
🔍 Vibe-Code Auditor v1.1

📁 분석 경로: examples\sample-project
🎯 분석 관점: 배포 관점

1️⃣ 프로젝트 언어 감지 중...
✓ 감지된 언어: python

2️⃣ 정적 분석 실행 중...
✓ 정적 분석 완료

3️⃣ AI 코드 리뷰 실행 중...
✓ AI 분석 완료

📋 분석 결과 리포트
(로그 없이 결과만 표시)
```

---

## 💡 실제 사용 예시

### 예시 1: 처음 사용 (Verbose 모드 권장)

```powershell
# 모든 로그를 보며 어떻게 작동하는지 확인
python -m src.cli.main --path . --mode deployment -v
```

### 예시 2: 일상적인 분석

```powershell
# 기본 모드로 필요한 정보만
python -m src.cli.main --path . --mode deployment
```

### 예시 3: 문제 디버깅

```powershell
# 에러 발생 시 verbose로 재실행
python -m src.cli.main --path . --mode deployment --verbose
```

### 예시 4: CI/CD 통합

```yaml
# GitHub Actions
- name: Code Audit
  run: |
    python -m src.cli.main --path . --mode deployment --quiet
```

---

## 🔍 로그에서 찾아야 할 것들

### ✅ 정상 작동 확인

**Verbose 모드에서:**
```
INFO     Running Pylint on ...
INFO     Pylint found X issues
INFO     Starting AI analysis...
INFO     Successfully received AI analysis response
```

### ⚠️ 경고 확인

```
WARNING  Pylint timed out after 300 seconds
WARNING  jscpd not installed
WARNING  Semgrep not available on Windows
```

→ 이런 경고는 분석은 계속되지만 일부 기능 제한

### ❌ 에러 확인

```
ERROR    Pylint executable not found in PATH
ERROR    Claude API connection error
ERROR    Failed to parse JSON output
```

→ 에러 발생 시 분석 일부 또는 전체 실패

---

## 📊 로그 분석 팁

### 1. 성능 확인

Verbose 모드에서 각 단계의 실행 시간 확인:

```
INFO     Pylint completed in 2.3s
INFO     Semgrep completed in 5.1s
INFO     AI analysis completed in 51.2s
```

→ 느린 부분 식별 가능

### 2. 문제 원인 파악

에러 발생 시 stacktrace 확인:

```
ERROR    Unexpected error during AI analysis: ...
         Traceback (most recent call last):
           File "...", line X, in analyze
             ...
```

### 3. 도구 설치 확인

```
WARNING  jscpd is not installed
         💡 npm install -g jscpd
```

→ 설치 힌트 제공

---

## 🎨 로그 색상 이해

- **🐛 DEBUG** (회색): 개발자용 세부 정보
- **ℹ️ INFO** (파란색): 일반 진행 상황
- **⚠️ WARNING** (노란색): 주의 필요
- **❌ ERROR** (빨간색): 오류 발생
- **🔴 CRITICAL** (진한 빨간색): 치명적 오류

---

## 🔧 로그 커스터마이징

### 환경변수로 로그 레벨 설정

```powershell
# PowerShell
$env:LOG_LEVEL = "DEBUG"
python -m src.cli.main --path . --mode deployment

# Linux/macOS
export LOG_LEVEL=DEBUG
python -m src.cli.main --path . --mode deployment
```

### 로그 파일로 저장

```powershell
# PowerShell
python -m src.cli.main --path . --mode deployment --verbose > analysis.log 2>&1

# Linux/macOS
python -m src.cli.main --path . --mode deployment --verbose 2>&1 | tee analysis.log
```

---

## ❓ FAQ

### Q: 로그가 너무 많아요
**A:** Quiet 모드 사용: `-q` 또는 `--quiet`

### Q: 로그가 안 보여요
**A:** Verbose 모드 사용: `-v` 또는 `--verbose`

### Q: CI/CD에서는 어떤 모드?
**A:** Quiet 모드 권장 (에러만 확인)

### Q: 디버깅할 때는?
**A:** Verbose 모드 필수

### Q: 일반 사용자는?
**A:** 기본 모드 (옵션 없이)

---

## 📚 다음 단계

- [빠른 시작 가이드](../QUICKSTART.md)
- [사용법](../USAGE.md)
- [문제 해결](../INSTALL-WINDOWS.md#문제-해결)

---

**로그를 통해 Vibe-Code Auditor의 작동을 더 잘 이해할 수 있습니다!** 🎯

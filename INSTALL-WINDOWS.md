# 🪟 Windows 설치 가이드

## ⚠️ Windows 환경 주의사항

Vibe-Code Auditor는 Windows에서도 작동하지만, 일부 정적 분석 도구가 제한됩니다:

- ✅ **작동**: Python 분석 (Pylint), AI 분석 (Claude), 코드 중복 감지 (jscpd)
- ❌ **미지원**: Semgrep (보안 스캔) - Windows 네이티브 미지원

---

## 🚀 빠른 설치 (Windows)

### 1단계: Python 환경 확인

```powershell
# Python 버전 확인 (3.11 이상 필요)
python --version

# pip 업그레이드
python -m pip install --upgrade pip
```

### 2단계: 의존성 설치

```powershell
cd "C:\Users\USER\Desktop\Vibe-Code Auditor"

# Windows용 패키지 설치
pip install -r requirements.txt
```

**설치 완료!** 이제 바로 사용할 수 있습니다.

---

## 🔧 설치 문제 해결

### 문제 1: Semgrep 설치 오류

```
Exception: Semgrep does not support Windows yet
```

**해결책**: `requirements.txt`에서 이미 Semgrep을 주석 처리했습니다. 다시 설치하세요:

```powershell
pip install -r requirements.txt
```

Semgrep 없이도 프로그램은 정상 작동하며, Windows 환경에서는 자동으로 건너뜁니다.

---

### 문제 2: Pylint 설치 오류

```powershell
# Pylint만 따로 설치
pip install pylint==3.3.2
```

---

### 문제 3: 모듈 import 오류

```
ModuleNotFoundError: No module named 'src'
```

**해결책**: 프로젝트 루트에서 실행하세요:

```powershell
# 프로젝트 루트 확인
cd "C:\Users\USER\Desktop\Vibe-Code Auditor"

# 실행
python -m src.cli.main --help
```

---

## 📦 선택적 도구 설치

### Node.js 기반 도구 (선택사항)

JavaScript/TypeScript 프로젝트를 분석하려면:

```powershell
# Node.js 설치 확인
node --version
npm --version

# ESLint 설치 (JavaScript/TypeScript 분석)
npm install -g eslint

# jscpd 설치 (코드 중복 감지)
npm install -g jscpd
```

---

## 🐧 완전한 기능을 원한다면: WSL 사용

Windows에서 모든 기능(Semgrep 포함)을 사용하려면 **WSL (Windows Subsystem for Linux)**을 설치하세요.

### WSL 설치 방법

```powershell
# PowerShell 관리자 권한으로 실행
wsl --install

# 재부팅 후 Ubuntu 설정
```

### WSL에서 Vibe-Code Auditor 설치

```bash
# WSL Ubuntu 터미널에서
cd /mnt/c/Users/USER/Desktop/Vibe-Code\ Auditor

# 전체 패키지 설치 (Semgrep 포함)
pip install -r requirements-full.txt

# 실행
python -m src.cli.main --path . --mode deployment
```

---

## ✅ 설치 확인

```powershell
# 도구 버전 확인
python -m src.cli.main --help

# 예제 프로젝트로 테스트
python -m src.cli.main --path examples/sample-project --mode deployment
```

**예상 출력:**
```
🔍 Vibe-Code Auditor v1.0

📁 분석 경로: examples/sample-project
🎯 분석 관점: 배포 관점
📊 우선순위: security, performance, scalability, ci_cd

1️⃣ 프로젝트 언어 감지 중...
✓ 감지된 언어: python
...
```

---

## 🎯 Windows에서 사용 가능한 기능

| 기능 | Windows | WSL/Linux |
|------|---------|-----------|
| Python 분석 (Pylint) | ✅ | ✅ |
| JavaScript 분석 (ESLint) | ✅ | ✅ |
| 코드 중복 (jscpd) | ✅ | ✅ |
| AI 분석 (Claude) | ✅ | ✅ |
| 보안 스캔 (Semgrep) | ❌ | ✅ |

---

## 💡 Windows 사용자를 위한 팁

### 1. PowerShell 별칭 만들기

```powershell
# PowerShell 프로필 편집
notepad $PROFILE

# 다음 내용 추가:
function vaudit { python -m src.cli.main $args }

# 저장 후 재시작
```

이제 간단하게 실행 가능:
```powershell
vaudit --path . --mode deployment
```

### 2. 배치 파일 생성

`vaudit.bat` 파일 생성:
```batch
@echo off
python -m src.cli.main %*
```

사용:
```powershell
.\vaudit.bat --path . --mode deployment
```

### 3. Windows Terminal 사용

Windows Terminal을 사용하면 컬러 출력이 더 예쁘게 표시됩니다.

---

## 🆘 추가 도움말

### API 키 설정

```powershell
# .env 파일 생성
copy .env.example .env

# 메모장으로 편집
notepad .env
```

`.env` 파일에 입력:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxx
```

### 자주 묻는 질문

**Q: Semgrep 없이도 보안 분석이 가능한가요?**
A: Pylint가 기본적인 코드 품질 검사를 하며, AI(Claude)가 보안 이슈를 일부 탐지합니다. 완전한 보안 스캔은 WSL을 사용하세요.

**Q: WSL 없이 Semgrep을 사용할 수 있나요?**
A: Docker Desktop for Windows를 사용하면 가능합니다:
```powershell
docker run --rm -v ${PWD}:/src semgrep/semgrep --config=auto /src
```

**Q: 실행 속도가 느려요**
A: `--skip-ai` 플래그를 사용하면 빠릅니다:
```powershell
python -m src.cli.main --path . --mode deployment --skip-ai
```

---

## 📚 다음 단계

1. ✅ [빠른 시작 가이드](QUICKSTART.md) 읽기
2. ✅ [사용 방법](USAGE.md) 학습
3. ✅ 실제 프로젝트에 적용하기

---

**Windows에서도 충분히 사용 가능합니다!** 🎉

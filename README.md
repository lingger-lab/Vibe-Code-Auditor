# 🔍 Vibe-Code Auditor

**바이브코딩으로 개발한 프로젝트를 AI + 정적 분석 도구로 자동 점검하는 멀티 인터페이스 코드 감사 플랫폼**

[![Version](https://img.shields.io/badge/version-1.10.0-blue.svg)](https://github.com/lingger-lab/Vibe-Code-Auditor)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

## 📋 주요 기능

### 🎯 핵심 기능
- ✅ **다국어 지원**: Python, JavaScript, TypeScript, Go, Rust, Java, PHP, C#, Ruby, Kotlin, Swift 등 11개 언어 지원
- 🤖 **AI 코드 리뷰**: Claude API를 활용한 주관적 코드 분석
- 🔒 **정적 분석**: Pylint, ESLint, Semgrep, staticcheck, clippy, PHPStan 등 15+ 도구 통합
- 🎯 **관점별 분석**: 배포 관점(보안, 성능) vs 자가 사용 관점(가독성, 유지보수성)
- 🖥️ **멀티 인터페이스**: CLI (개발자용) + Web UI (모든 사용자용)
- 📊 **시각화**: 인터랙티브 차트 및 실시간 진행 상황 표시
- 💾 **결과 캐싱**: 99% 속도 향상 (변경되지 않은 파일 재분석 방지)
- 📈 **히스토리 추적**: 분석 결과 추이 관리 및 트렌드 분석

### ✨ v1.10.0 새로운 기능
- 📦 **실행 파일 배포**: PyInstaller 기반 독립 실행형 .exe (설치 불필요)
- 📄 **PDF 리포트**: 전문적인 PDF 형식 분석 보고서 생성
- 🔄 **비교 모드**: 두 분석 결과 비교 및 품질 개선 추적
- 🌳 **폴더 트리 뷰어**: 프로젝트 구조 및 분석 대상 파일 시각화
- 📂 **빠른 경로 선택**: 바탕화면, 문서 폴더 원클릭 접근
- 📊 **페이지네이션**: 대량 이슈 목록 효율적 탐색 (10/20/50/100개씩)

## 🚀 빠른 시작

### 방법 1: 실행 파일 사용 (권장 - 설치 불필요)

```bash
# 1. Releases에서 다운로드
# https://github.com/lingger-lab/Vibe-Code-Auditor/releases

# 2. 압축 해제 후 실행
# Windows: dist\VibeAuditor.exe 더블클릭
# Linux/Mac: ./dist/VibeAuditor

# 3. 메뉴에서 선택
# 1: CLI 모드
# 2: UI 모드 (웹 브라우저 자동 실행)
# 3: 종료
```

### 방법 2: Python 소스 코드 실행

#### 1단계: 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# .env 파일 설정 (AI 분석 사용 시)
cp .env.example .env
# .env 파일을 열어 ANTHROPIC_API_KEY 입력
```

#### 2단계: 사용법

##### 🎯 통합 런처 (CLI/UI 선택)

```bash
# 대화형 메뉴
python vibe_auditor.py

# 메뉴가 표시되면 선택:
# 1 → CLI 모드
# 2 → UI 모드
# 3 → 종료
```

##### 🖥️ UI 모드 (권장 - 모든 사용자용)

```bash
# 방법 1: Python 스크립트
python run_ui.py

# 방법 2: Windows 더블클릭
run_ui.bat

# 방법 3: 통합 런처
python vibe_auditor.py  # 메뉴에서 2 선택

# 브라우저에서 자동으로 열립니다!
# 3-클릭만으로 분석 완료: 폴더 선택 → 설정 → 시작
```

##### 💻 CLI 모드 (개발자용)

**배포 관점 분석 (보안, 성능, 확장성 우선)**
```bash
python -m src.cli.main --path /path/to/your/project --mode deployment

# 또는 통합 런처 사용
python vibe_auditor.py --path /path/to/your/project --mode deployment
```

**자가 사용 관점 분석 (가독성, 유지보수성 우선)**
```bash
python -m src.cli.main --path /path/to/your/project --mode personal
```

**AI 분석 건너뛰기 (정적 분석만 수행)**
```bash
python -m src.cli.main --path /path/to/your/project --mode deployment --skip-ai
```

## 📦 필수 요구사항

### Python 패키지
- Python 3.11+
- click==8.1.7
- anthropic==0.45.0
- rich==13.9.4
- python-dotenv==1.0.1
- pylint==3.3.2
- semgrep==1.100.0 **(Linux/macOS/WSL만 지원)**

### 🪟 Windows 사용자 주의
- **Semgrep은 Windows를 네이티브로 지원하지 않습니다**
- Windows에서는 Semgrep 없이도 정상 작동합니다
- 완전한 기능을 원하면 WSL(Windows Subsystem for Linux) 사용 권장
- 자세한 내용: [Windows 설치 가이드](INSTALL-WINDOWS.md)

### 외부 도구 (선택적)
- **Node.js**: ESLint, jscpd 사용 시
  ```bash
  npm install -g eslint jscpd
  ```

### API 키
- **Anthropic API Key**: Claude Code API 사용을 위해 필수
  - [Anthropic Console](https://console.anthropic.com/)에서 발급

## 🏗️ 프로젝트 구조

```
vibe-auditor/
├── src/
│   ├── cli/
│   │   └── main.py           # Click 기반 CLI 진입점
│   ├── analyzers/
│   │   ├── ai_analyzer.py    # Claude Code API 호출
│   │   ├── static_analyzer.py # 정적 분석 도구 실행
│   ├── detectors/
│   │   └── language_detector.py # 프로젝트 언어 자동 감지
│   ├── reporters/
│   │   └── cli_reporter.py   # Rich 기반 터미널 출력
│   └── config/
│       └── settings.py       # 분석 규칙 및 우선순위 설정
├── docs/
│   ├── PRD.md               # 요구사항 정의서
│   ├── TRD.md               # 기술 사양서
│   └── Tasks.md             # 개발 착수 프롬프트
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## 🎯 분석 관점

### 배포 관점 (deployment)
- **우선순위**: 보안, 성능, 확장성, CI/CD 검증
- **분석 도구**: Semgrep (보안 스캔), Pylint (코드 품질)
- **적용 대상**: 배포 전 프로젝트, 프로덕션 코드

### 자가 사용 관점 (personal)
- **우선순위**: 가독성, 유지보수성, 코드 중복 제거
- **분석 도구**: jscpd (중복 감지), Pylint (스타일 검사)
- **적용 대상**: 개인 프로젝트, 학습용 코드

## 📊 출력 예시

```
🔍 Vibe-Code Auditor v1.0

📁 분석 경로: /path/to/project
🎯 분석 관점: 배포 관점
📊 우선순위: security, performance, scalability, ci_cd

1️⃣ 프로젝트 언어 감지 중...
✓ 감지된 언어: python, javascript

2️⃣ 정적 분석 실행 중...
✓ 정적 분석 완료

3️⃣ AI 코드 리뷰 실행 중...
✓ AI 분석 완료

📋 분석 결과 리포트

┌─────────────────────┐
│   분석 요약         │
├─────────────────────┤
│ 정적 분석 이슈: 15  │
│  🔴 Critical: 2     │
│  🟡 Warning: 8      │
│  🟢 Info: 5         │
└─────────────────────┘

━━━ 정적 분석 결과 ━━━

🔴 CRITICAL (2)
  • SQL Injection vulnerability detected
    위치: src/database.py:45
  • Hardcoded credentials found
    위치: config/settings.py:12

🟡 WARNING (8)
  • Code duplication detected (15%)
  • Function complexity exceeds threshold
    위치: src/utils.py:128
  ...

━━━ AI 코드 리뷰 결과 ━━━

🔴 CRITICAL (1)
  ▸ 입력 검증 누락
    - 파일: api/routes.py
    - 설명: 사용자 입력을 검증 없이 직접 데이터베이스 쿼리에 사용
    - 제안: Parameterized query 사용 또는 ORM 활용

━━━ 권장 사항 ━━━
  • 🔒 Critical 보안 이슈를 최우선으로 해결하세요
  • ⚡ 성능 관련 Warning을 검토하세요
  • 🔄 CI/CD 파이프라인에 정적 분석 도구를 통합하세요
  • 📝 배포 전 모든 Critical 이슈를 해결하세요

✅ 분석 완료!
```

## 🛠️ 문제 해결

### API 키 오류
```
❌ 오류: ANTHROPIC_API_KEY가 설정되지 않았습니다.
```
- `.env` 파일에 `ANTHROPIC_API_KEY=your_key` 추가
- 또는 `--skip-ai` 플래그 사용

### 분석 도구 미설치
```
⚠ Pylint is not installed
💡 pip install pylint==3.3.2
```
- 제안된 명령어로 도구 설치

### 권한 오류
- 분석 대상 폴더에 읽기 권한이 있는지 확인

## 📚 참고 자료

- [요구사항 정의서 (PRD)](docs/PRD.md)
- [기술 사양서 (TRD)](docs/TRD.md)
- [개발 착수 프롬프트 (Tasks)](docs/Tasks.md)
- [Phase 3 완료 보고서](docs/PHASE_3_COMPLETE.md)

## 🔨 빌드 및 배포

### 자동화된 빌드

**Windows:**
```bash
# 빌드 스크립트 실행
build.bat

# 또는 수동 빌드
pyinstaller VibeAuditor.spec
```

**Linux/Mac:**
```bash
# 실행 권한 부여
chmod +x build.sh

# 빌드 스크립트 실행
./build.sh

# 또는 수동 빌드
pyinstaller VibeAuditor.spec
```

### 빌드 결과

빌드가 완료되면 `dist/` 폴더에 실행 파일이 생성됩니다:

```
dist/
├── VibeAuditor.exe      # Windows 실행 파일 (~150-200MB)
├── VibeAuditor          # Linux/Mac 실행 파일
└── _internal/           # 내부 라이브러리 및 의존성
```

### 배포 방법

1. **단일 파일 배포 (권장)**
   ```bash
   # dist 폴더 전체를 압축
   # Windows: zip 또는 7-Zip 사용
   # Linux/Mac: tar -czf VibeAuditor.tar.gz dist/
   ```

2. **GitHub Release 생성**
   - Releases 탭에서 새 릴리스 생성
   - 압축 파일 업로드
   - 버전 태그 지정 (예: v1.9.0)

3. **사용자에게 전달**
   - 압축 해제 후 실행 파일 더블클릭
   - 설치 과정 없이 바로 사용 가능

### 빌드 요구사항

- PyInstaller 6.17.0+
- 모든 프로젝트 의존성 설치됨
- Windows: Visual C++ Redistributable (대부분 시스템에 설치됨)

## 🤝 기여

이 프로젝트는 바이브코딩 방법론으로 개발되었습니다.

## 📄 라이선스

MIT License

## 🔗 관련 링크

- [Claude Code API Documentation](https://docs.anthropic.com/claude/docs)
- [Semgrep Rules](https://semgrep.dev/r)
- [Pylint Documentation](https://pylint.pycqa.org/)
- [jscpd GitHub](https://github.com/kucherenko/jscpd)

---

**만든 이**: Vibe Coding Architect V3.0
**버전**: 1.9.0
**최종 업데이트**: 2025-12-02

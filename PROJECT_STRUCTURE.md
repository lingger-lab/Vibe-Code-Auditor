# 프로젝트 구조

## 📁 디렉토리 구조

```
Vibe-Code Auditor/
│
├── 📄 README.md                    # 프로젝트 소개 및 기본 사용법
├── 📄 INSTALL.md                   # 설치 가이드
├── 📄 USAGE.md                     # 상세 사용 가이드
├── 📄 PROJECT_STRUCTURE.md         # 이 파일
├── 📄 requirements.txt             # Python 의존성 목록
├── 📄 setup.py                     # 패키지 설치 스크립트
├── 📄 .env.example                 # 환경변수 예제
├── 📄 .gitignore                   # Git 제외 파일 목록
│
├── 📂 docs/                        # 설계 문서
│   ├── PRD.md                      # 요구사항 정의서
│   ├── TRD.md                      # 기술 사양서
│   ├── Tasks.md                    # AI 코딩 착수 프롬프트
│   ├── PHASE_1_COMPLETE.md         # Phase 1 완료 문서 (v1.6.0)
│   ├── PHASE_2.1_COMPLETE.md       # Phase 2.1 완료 문서 (v1.5.0)
│   └── IMPROVEMENT_ROADMAP.md      # 개선 로드맵
│
├── 📂 src/                         # 소스 코드
│   ├── __init__.py
│   │
│   ├── 📂 core/                    # 코어 엔진 (v1.6.0 추가)
│   │   ├── __init__.py
│   │   └── analyzer_engine.py      # 통합 분석 엔진
│   │
│   ├── 📂 cli/                     # CLI 인터페이스
│   │   ├── __init__.py
│   │   └── main.py                 # Click 기반 메인 CLI
│   │
│   ├── 📂 analyzers/               # 분석 엔진
│   │   ├── __init__.py
│   │   ├── ai_analyzer.py          # Claude API 연동
│   │   └── static_analyzer.py      # 11개 언어 정적 분석 도구
│   │
│   ├── 📂 detectors/               # 언어 감지
│   │   ├── __init__.py
│   │   └── language_detector.py    # 프로젝트 언어 자동 감지
│   │
│   ├── 📂 reporters/               # 리포트 생성
│   │   ├── __init__.py
│   │   ├── cli_reporter.py         # Rich 기반 터미널 출력
│   │   ├── json_reporter.py        # JSON 형식 출력
│   │   └── html_reporter.py        # HTML 형식 출력
│   │
│   ├── 📂 utils/                   # 유틸리티
│   │   ├── __init__.py
│   │   ├── cache_manager.py        # 결과 캐싱
│   │   ├── history_tracker.py      # 히스토리 추적
│   │   └── logger.py               # 로깅 설정
│   │
│   └── 📂 config/                  # 설정
│       ├── __init__.py
│       ├── settings.py             # 전역 설정 및 상수
│       └── config_loader.py        # YAML 설정 로더
│
├── 📂 tests/                       # 테스트 (99개 테스트)
│   ├── __init__.py
│   ├── test_ai_analyzer.py         # AI 분석 테스트
│   ├── test_cache_manager.py       # 캐시 테스트
│   ├── test_cli.py                 # CLI 테스트
│   ├── test_config_loader.py       # 설정 로더 테스트
│   ├── test_history_tracker.py     # 히스토리 테스트
│   ├── test_integration.py         # 통합 테스트
│   └── test_language_detector.py   # 언어 감지 테스트
│
└── 📂 examples/                    # 예제 프로젝트
    ├── README.md
    ├── sample-project/
    │   └── app.py                  # 테스트용 샘플 코드
    └── test-project/
        ├── sample.py
        └── .vibe-auditor.yml       # 설정 파일 예제
```

## 🔧 주요 모듈 설명

### 1. Core 모듈 (`src/core/`) - v1.6.0 추가

**analyzer_engine.py**
- 통합 분석 엔진 (CLI/UI 공유)
- 분석 파이프라인 오케스트레이션
- Progress callback 지원
- 요구사항 검증 및 에러 처리
- 히스토리/캐시 관리

**주요 클래스:**
- `AnalyzerEngine`: 통합 분석 엔진
- `AnalysisProgress`: 진행 상황 추적

### 2. CLI 모듈 (`src/cli/`)

**main.py**
- Click 기반 CLI 진입점
- 사용자 입력 처리 (경로, 모드, 옵션)
- AnalyzerEngine 활용
- Progress callback 구현
- Rich 기반 실시간 진행 상황 표시

### 3. Analyzers 모듈 (`src/analyzers/`)

**ai_analyzer.py**
- Claude API 호출
- 코드 샘플 수집 및 전처리 (11개 언어)
- AI 프롬프트 생성
- AI 응답 파싱 및 구조화

**static_analyzer.py**
- 15+ 정적 분석 도구 실행
- 11개 언어 지원 (Python, JS, TS, Go, Rust, PHP, Ruby, Kotlin, Swift, C#, Java)
- 도구 설치 여부 확인
- 분석 결과 통합 및 정규화
- 심각도 매핑

### 4. Detectors 모듈 (`src/detectors/`)

**language_detector.py**
- 파일 확장자 기반 언어 감지 (11개 언어)
- 특수 파일 감지 (package.json, requirements.txt, go.mod, Cargo.toml 등)
- 제외 패턴 필터링
- 프로젝트 요약 생성

### 5. Reporters 모듈 (`src/reporters/`)

**cli_reporter.py**
- Rich 라이브러리 기반 포맷팅
- 심각도별 색상 구분 출력
- 요약 테이블 생성
- 관점별 우선순위 정렬

**json_reporter.py**
- JSON 형식 리포트 생성
- 구조화된 데이터 출력

**html_reporter.py**
- HTML 형식 리포트 생성
- 인터랙티브 웹 리포트

### 6. Utils 모듈 (`src/utils/`)

**cache_manager.py**
- 해시 기반 결과 캐싱
- TTL 기반 캐시 만료
- 99% 속도 향상

**history_tracker.py**
- 분석 결과 히스토리 추적
- 트렌드 분석 (개선/악화/안정)
- 시계열 데이터 관리

**logger.py**
- 로깅 설정 및 관리
- 파일/콘솔 로그 출력

### 7. Config 모듈 (`src/config/`)

**settings.py**
- 환경변수 로드 (.env)
- 분석 모드 설정 (deployment, personal)
- 11개 언어 패턴 정의
- 15+ 정적 분석 도구 설정
- 심각도 레벨 정의

**config_loader.py**
- YAML 설정 파일 로드
- 기본 설정 병합
- 설정 검증

## 🔄 데이터 흐름 (v1.6.0)

```
1. 사용자 입력
   └─> CLI (main.py)
       └─> AnalyzerEngine 생성 (progress_callback 등록)

2. AnalyzerEngine.analyze()
   │
   ├─> 1단계: validate_requirements()
   │   ├─> 프로젝트 경로 확인
   │   └─> API 키 확인 (AI 분석 시)
   │
   ├─> 2단계: LanguageDetector.detect()
   │   └─> 11개 언어 감지
   │       └─> Progress callback (20%)
   │
   ├─> 3단계: StaticAnalyzer.analyze()
   │   ├─> Pylint, Ruff (Python)
   │   ├─> ESLint, TSLint (JavaScript/TypeScript)
   │   ├─> staticcheck, golangci-lint (Go)
   │   ├─> clippy, cargo-audit (Rust)
   │   ├─> PHPStan, Psalm (PHP)
   │   ├─> RuboCop (Ruby)
   │   ├─> ktlint (Kotlin)
   │   ├─> SwiftLint (Swift)
   │   ├─> Roslyn (C#)
   │   ├─> Semgrep (보안)
   │   └─> jscpd (중복)
   │       └─> Progress callback (60%)
   │
   ├─> 4단계: AIAnalyzer.analyze() (선택적)
   │   ├─> 코드 샘플 수집 (11개 언어)
   │   ├─> Claude API 호출
   │   └─> AI 분석 결과
   │       └─> Progress callback (90%)
   │
   ├─> 5단계: HistoryTracker.save_result() (선택적)
   │   └─> 분석 결과 저장
   │       └─> Progress callback (95%)
   │
   └─> 6단계: 결과 반환
       └─> Progress callback (100%)

3. 리포트 생성
   └─> CLIReporter / JSONReporter / HTMLReporter
       ├─> 결과 통합
       ├─> 관점별 필터링
       └─> 출력
```

## 🎨 설계 패턴

### 1. 전략 패턴 (Strategy Pattern)
- 분석 관점(deployment/personal)에 따라 다른 우선순위 적용
- 언어별 다른 분석 도구 선택

### 2. 파사드 패턴 (Facade Pattern)
- `main.py`가 복잡한 분석 프로세스를 간단한 인터페이스로 제공
- 사용자는 `--path`와 `--mode`만 지정

### 3. 팩토리 패턴 (Factory Pattern)
- 언어 감지 결과에 따라 적절한 분석 도구 생성

### 4. 빌더 패턴 (Builder Pattern)
- AI 프롬프트를 단계별로 구성
- 리포트를 섹션별로 구성

## 📊 의존성 그래프 (v1.6.0)

```
main.py
└─> analyzer_engine.py (코어 엔진)
    ├─> language_detector.py
    │   └─> settings.py
    ├─> static_analyzer.py
    │   └─> settings.py
    ├─> ai_analyzer.py
    │   └─> settings.py
    ├─> history_tracker.py
    └─> cache_manager.py

main.py
└─> cli_reporter.py / json_reporter.py / html_reporter.py
    └─> settings.py
```

## 🔐 보안 고려사항

1. **API 키 관리**
   - `.env` 파일로 분리
   - `.gitignore`에 포함
   - 절대 코드에 하드코딩하지 않음

2. **입력 검증**
   - 파일 경로 존재 여부 확인
   - 허용된 분석 모드만 수락

3. **샌드박싱**
   - 분석 도구 실행 시 타임아웃 설정
   - 에러 처리로 악의적 입력 방지

## 📈 확장 가능성

### 추가 가능한 기능
1. **추가 언어 지원**
   - `settings.py`의 `LANGUAGE_PATTERNS`에 추가

2. **새로운 분석 도구**
   - `static_analyzer.py`에 메서드 추가
   - `settings.py`에 도구 설정 추가

3. **리포트 형식**
   - `reporters/` 폴더에 새 리포터 추가
   - (예: `html_reporter.py`, `pdf_reporter.py`)

4. **Git 통합**
   - `analyzers/git_analyzer.py` 추가
   - 변경된 파일만 분석

## 🧪 테스트 전략

### 현재 구현
- 유닛 테스트: `test_language_detector.py`

### 추가 가능한 테스트
- `test_static_analyzer.py`: 정적 분석 테스트
- `test_ai_analyzer.py`: AI 분석 Mock 테스트
- `test_cli_reporter.py`: 리포트 출력 테스트
- 통합 테스트: 전체 워크플로우 테스트

## 📝 개발 가이드

### 새 기능 추가 시
1. `docs/PRD.md` 업데이트
2. `docs/TRD.md`에 기술 사양 추가
3. 해당 모듈 구현
4. 테스트 작성
5. `README.md` 업데이트

### 코드 스타일
- PEP 8 준수
- Docstring 작성 (Google 스타일)
- Type hints 사용
- 의미 있는 변수/함수명

### 버전 관리
- Semantic Versioning (MAJOR.MINOR.PATCH)
- 현재 버전: 1.6.0
- v1.5.0: 11개 언어 지원, 15+ 정적 분석 도구
- v1.6.0: 코어 엔진 리팩토링, 멀티 인터페이스 지원 준비

## 🚀 Phase 1 완료 (v1.6.0)

### 주요 성과
- ✅ 코어 엔진 분리 (`src/core/analyzer_engine.py`)
- ✅ CLI 리팩토링 (AnalyzerEngine 사용)
- ✅ Progress callback 시스템 구현
- ✅ 모든 테스트 통과 (99/99)
- ✅ 하위 호환성 유지

### 아키텍처 개선
```
기존 (v1.5.0):          새로운 (v1.6.0):
CLI (단일)              CLI + (향후) UI
  ↓                       ↓        ↓
분석 로직               AnalyzerEngine (공유)
                           ↓
                      분석 로직
```

### 다음 단계: Phase 2
- Streamlit UI 구현
- UI 전용 리포터
- PyInstaller 패키징

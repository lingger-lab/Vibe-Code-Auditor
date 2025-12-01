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
│   └── Tasks.md                    # AI 코딩 착수 프롬프트
│
├── 📂 src/                         # 소스 코드
│   ├── __init__.py
│   │
│   ├── 📂 cli/                     # CLI 진입점
│   │   ├── __init__.py
│   │   └── main.py                 # Click 기반 메인 CLI
│   │
│   ├── 📂 analyzers/               # 분석 엔진
│   │   ├── __init__.py
│   │   ├── ai_analyzer.py          # Claude Code API 연동
│   │   └── static_analyzer.py      # 정적 분석 도구 실행
│   │
│   ├── 📂 detectors/               # 언어 감지
│   │   ├── __init__.py
│   │   └── language_detector.py    # 프로젝트 언어 자동 감지
│   │
│   ├── 📂 reporters/               # 리포트 생성
│   │   ├── __init__.py
│   │   └── cli_reporter.py         # Rich 기반 터미널 출력
│   │
│   └── 📂 config/                  # 설정
│       ├── __init__.py
│       └── settings.py             # 전역 설정 및 상수
│
├── 📂 tests/                       # 테스트
│   ├── __init__.py
│   └── test_language_detector.py   # 언어 감지 테스트
│
└── 📂 examples/                    # 예제 프로젝트
    ├── README.md
    └── sample-project/
        └── app.py                  # 테스트용 샘플 코드
```

## 🔧 주요 모듈 설명

### 1. CLI 모듈 (`src/cli/`)

**main.py**
- Click 기반 CLI 진입점
- 사용자 입력 처리 (경로, 모드, 옵션)
- 분석 워크플로우 오케스트레이션
- 에러 핸들링 및 사용자 피드백

### 2. Analyzers 모듈 (`src/analyzers/`)

**ai_analyzer.py**
- Claude Code API 호출
- 코드 샘플 수집 및 전처리
- AI 프롬프트 생성
- AI 응답 파싱 및 구조화

**static_analyzer.py**
- 정적 분석 도구 실행 (Pylint, Semgrep, jscpd)
- 도구 설치 여부 확인
- 분석 결과 통합 및 정규화
- 심각도 매핑

### 3. Detectors 모듈 (`src/detectors/`)

**language_detector.py**
- 파일 확장자 기반 언어 감지
- 특수 파일 감지 (package.json, requirements.txt 등)
- 제외 패턴 필터링
- 프로젝트 요약 생성

### 4. Reporters 모듈 (`src/reporters/`)

**cli_reporter.py**
- Rich 라이브러리 기반 포맷팅
- 심각도별 색상 구분 출력
- 요약 테이블 생성
- 관점별 우선순위 정렬

### 5. Config 모듈 (`src/config/`)

**settings.py**
- 환경변수 로드 (.env)
- 분석 모드 설정 (deployment, personal)
- 언어 패턴 정의
- 정적 분석 도구 설정
- 심각도 레벨 정의

## 🔄 데이터 흐름

```
1. 사용자 입력
   └─> CLI (main.py)

2. 언어 감지
   └─> LanguageDetector
       └─> 감지된 언어 목록

3. 정적 분석
   └─> StaticAnalyzer
       ├─> Pylint (Python)
       ├─> ESLint (JavaScript/TypeScript)
       ├─> Semgrep (보안)
       └─> jscpd (중복)
       └─> 정적 분석 결과

4. AI 분석 (선택적)
   └─> AIAnalyzer
       ├─> 코드 샘플 수집
       ├─> Claude API 호출
       └─> AI 분석 결과

5. 리포트 생성
   └─> CLIReporter
       ├─> 결과 통합
       ├─> 관점별 필터링
       └─> 터미널 출력
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

## 📊 의존성 그래프

```
main.py
├─> language_detector.py
├─> static_analyzer.py
│   └─> settings.py
├─> ai_analyzer.py
│   └─> settings.py
└─> cli_reporter.py
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
- 현재 버전: 1.0.0

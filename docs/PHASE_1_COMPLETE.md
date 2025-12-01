# Phase 1 완료: 코어 엔진 리팩토링

## 개요

Phase 1에서는 기존 CLI에 통합되어 있던 분석 로직을 독립적인 코어 엔진으로 분리했습니다. 이를 통해 향후 UI 모드 추가 시 CLI와 UI가 동일한 분석 엔진을 공유할 수 있는 구조를 마련했습니다.

## 주요 변경사항

### 1. 새로운 코어 모듈 생성

**위치**: `src/core/`

새로운 `core` 패키지를 생성하여 분석 엔진의 핵심 로직을 관리합니다.

#### 파일 구조
```
src/core/
├── __init__.py
└── analyzer_engine.py
```

### 2. AnalyzerEngine 클래스

**파일**: `src/core/analyzer_engine.py`

통합 분석 엔진을 제공하는 핵심 클래스입니다.

#### 주요 기능

##### 초기화 파라미터
```python
AnalyzerEngine(
    project_path: Path,           # 분석할 프로젝트 경로
    mode: str = 'deployment',     # 분석 모드
    skip_ai: bool = False,        # AI 분석 건너뛰기 여부
    use_cache: bool = True,       # 캐시 사용 여부
    save_history: bool = True,    # 히스토리 저장 여부
    progress_callback: Optional[Callable] = None  # 진행 상황 콜백
)
```

##### 핵심 메서드

1. **validate_requirements()** - 분석 실행 전 요구사항 검증
   - 프로젝트 경로 유효성 확인
   - API 키 설정 확인 (AI 분석 시)
   - 반환: `(is_valid: bool, error_message: Optional[str])`

2. **analyze()** - 전체 분석 파이프라인 실행
   - 언어 감지 (LanguageDetector)
   - 정적 분석 (StaticAnalyzer)
   - AI 분석 (AIAnalyzer, 선택적)
   - 히스토리 저장 (HistoryTracker, 선택적)
   - 반환: 분석 결과 딕셔너리

3. **get_trend_data()** - 히스토리 추세 데이터 조회
   - 프로젝트의 과거 분석 기록 반환
   - 트렌드 분석 (개선/악화/안정)

4. **clear_cache()** - 캐시 데이터 삭제
   - 프로젝트의 캐시된 분석 결과 제거

#### AnalysisProgress 클래스

분석 진행 상황을 추적하기 위한 데이터 컨테이너입니다.

```python
class AnalysisProgress:
    stage: str              # 현재 단계
    message: str            # 진행 메시지
    percentage: int         # 진행률 (0-100)
    languages: List[str]    # 감지된 언어
    static_results: Dict    # 정적 분석 결과
    ai_results: Dict        # AI 분석 결과
    completed: bool         # 완료 여부
    error: Optional[str]    # 에러 메시지
```

### 3. CLI 리팩토링

**파일**: `src/cli/main.py`

기존 CLI를 새로운 `AnalyzerEngine`을 사용하도록 리팩토링했습니다.

#### 변경 전 (v1.5.0)
```python
# 직접 각 컴포넌트 호출
detector = LanguageDetector(path)
languages = detector.detect()

static_analyzer = StaticAnalyzer(path, languages, mode)
static_results = static_analyzer.analyze()

ai_analyzer = AIAnalyzer(path, mode)
ai_results = ai_analyzer.analyze()

history_tracker = HistoryTracker(path)
history_tracker.save_result(mode, static_results, ai_results)
```

#### 변경 후 (v1.6.0)
```python
# 통합 엔진 사용
engine = AnalyzerEngine(
    project_path=path,
    mode=mode,
    skip_ai=skip_ai,
    use_cache=use_cache,
    save_history=save_history,
    progress_callback=progress_callback
)

result = engine.analyze()
languages = result['languages']
static_results = result['static_results']
ai_results = result['ai_results']
```

#### Progress Callback 구현

CLI는 `progress_callback`을 통해 실시간 진행 상황을 표시합니다:

```python
def progress_callback(progress: AnalysisProgress):
    """Handle progress updates from the analyzer engine."""
    if progress.stage == "detection" and progress.percentage == 20:
        console.print(f"[green]✓ 감지된 언어:[/green] {', '.join(progress.languages)}\n")
    elif progress.stage == "static_analysis" and progress.percentage == 60:
        console.print(f"[green]✓ 정적 분석 완료[/green]\n")
    # ... 기타 단계별 처리
```

### 4. 의존성 간소화

CLI의 직접 의존성이 줄어들었습니다:

**제거된 import**:
- `ANTHROPIC_API_KEY` (엔진이 내부적으로 처리)
- `LanguageDetector` (엔진 내부 사용)
- `StaticAnalyzer` (엔진 내부 사용)
- `AIAnalyzer` (엔진 내부 사용)
- `HistoryTracker` (엔진 내부 사용)
- `CacheManager` (엔진 내부 사용)

**새로 추가된 import**:
- `AnalyzerEngine`
- `AnalysisProgress`

## 아키텍처 다이어그램

### 기존 구조 (v1.5.0)
```
┌─────────────┐
│   CLI Main  │
└──────┬──────┘
       │
       ├──> LanguageDetector
       ├──> StaticAnalyzer
       ├──> AIAnalyzer
       ├──> HistoryTracker
       └──> CacheManager
```

### 새로운 구조 (v1.6.0)
```
┌─────────────┐
│   CLI Main  │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ AnalyzerEngine   │ ◄─── 공유 가능한 코어 엔진
└────────┬─────────┘
         │
         ├──> LanguageDetector
         ├──> StaticAnalyzer
         ├──> AIAnalyzer
         ├──> HistoryTracker
         └──> CacheManager
```

### 향후 구조 (Phase 2 이후)
```
┌─────────────┐         ┌─────────────┐
│   CLI Main  │         │  UI (Streamlit) │
└──────┬──────┘         └──────┬──────┘
       │                        │
       └────────┬───────────────┘
                ▼
        ┌──────────────────┐
        │ AnalyzerEngine   │ ◄─── 공유 코어 엔진
        └────────┬─────────┘
                 │
                 ├──> LanguageDetector
                 ├──> StaticAnalyzer
                 ├──> AIAnalyzer
                 ├──> HistoryTracker
                 └──> CacheManager
```

## 테스트 결과

모든 기존 테스트가 통과했습니다:

```
======================== 99 passed in 71.88s ========================
Coverage: 66%
```

### 주요 테스트 항목
- ✅ CLI 모든 옵션 동작 확인
- ✅ 분석 파이프라인 통합 테스트
- ✅ 캐싱 워크플로우
- ✅ 히스토리 추적
- ✅ 에러 핸들링

## 이점

### 1. 코드 재사용성
- CLI와 향후 UI가 동일한 분석 로직 공유
- 중복 코드 제거
- 유지보수 용이성 향상

### 2. 관심사의 분리 (Separation of Concerns)
- **코어 엔진**: 분석 로직만 담당
- **CLI/UI**: 사용자 인터페이스만 담당
- **리포터**: 결과 출력만 담당

### 3. 테스트 용이성
- 엔진을 독립적으로 테스트 가능
- 인터페이스별 테스트 분리 가능
- Mock/Stub 작성 용이

### 4. 확장성
- 새로운 인터페이스(UI, API 등) 쉽게 추가 가능
- 엔진 기능 확장 시 모든 인터페이스에 자동 반영
- Progress callback으로 다양한 UI 패턴 지원

### 5. 에러 처리 개선
- 중앙화된 에러 처리
- 진행 상황 추적을 통한 디버깅 용이
- 일관된 에러 메시지

## 하위 호환성

- ✅ 모든 기존 CLI 옵션 정상 동작
- ✅ 기존 테스트 100% 통과
- ✅ 출력 형식 동일
- ✅ 설정 파일 형식 동일

## 향후 작업 (Phase 2)

Phase 1 완료 후 다음 단계:

1. **Streamlit UI 구현** (`src/interfaces/ui/`)
   - 파일/폴더 선택 UI
   - 실시간 진행 상황 표시 (progress callback 활용)
   - 결과 시각화 (차트, 테이블)
   - 히스토리 트렌드 그래프

2. **UI 전용 리포터** (`src/reporters/ui_reporter.py`)
   - Streamlit 컴포넌트 기반 출력
   - 인터랙티브 차트/그래프
   - 필터링 및 검색 기능

3. **PyInstaller 패키징**
   - 실행 파일 생성 (.exe)
   - 모드 선택 런처 (CLI/UI)

## 파일 변경 요약

### 새로 추가된 파일
- `src/core/__init__.py`
- `src/core/analyzer_engine.py`

### 수정된 파일
- `src/cli/main.py` (리팩토링)

### 변경 통계
- **추가**: ~300 라인 (코어 엔진)
- **제거**: ~80 라인 (CLI 중복 코드)
- **수정**: ~100 라인 (CLI 리팩토링)

## 결론

Phase 1을 통해 Vibe-Code Auditor는 단일 인터페이스(CLI) 도구에서 **멀티 인터페이스 플랫폼**으로 발전할 수 있는 기반을 마련했습니다.

코어 엔진 분리로 인해:
- 코드 품질 향상
- 유지보수성 개선
- 확장성 확보
- 테스트 용이성 증가

모든 기존 기능은 하위 호환성을 유지하며, Phase 2에서 UI 모드를 추가할 준비가 완료되었습니다.

---

**완료 일자**: 2025-12-01
**테스트 통과율**: 100% (99/99)
**코드 커버리지**: 66%
**다음 단계**: Phase 2 - Streamlit UI 구현

# 📋 AI 분석 대상 파일 선정 로직 문서

## 개요

Claude API에 요청할 프로젝트 파일을 선정하는 로직은 `src/analyzers/ai_analyzer.py`의 `_collect_code_samples()` 메서드에서 구현되어 있습니다.

## 파일 선정 프로세스

### 1단계: 파일 필터링

#### 1.1 제외 디렉토리 필터링
다음 디렉토리는 자동으로 제외됩니다:
```python
exclude_dirs = {
    'node_modules',  # Node.js 의존성
    'venv',          # Python 가상환경
    '.venv',         # Python 가상환경 (다른 이름)
    '.git',          # Git 저장소
    '__pycache__',  # Python 캐시
    'build',         # 빌드 결과물
    'dist',          # 배포 파일
    'target',        # 빌드 타겟 (Java/Maven)
    'vendor'         # 의존성 (Go/PHP)
}
```

**로직**: 파일 경로의 어느 부분에든 제외 디렉토리 이름이 포함되면 제외

#### 1.2 파일 확장자 필터링
다음 확장자만 분석 대상으로 포함됩니다:
```python
file_extensions = {
    '.py',           # Python
    '.js', '.jsx',   # JavaScript
    '.ts', '.tsx',   # TypeScript
    '.go',           # Go
    '.rs',           # Rust
    '.java',         # Java
    '.kt', '.kts',   # Kotlin
    '.php',          # PHP
    '.cs',           # C#
    '.rb',           # Ruby
    '.swift'         # Swift
}
```

**로직**: 파일 확장자가 위 목록에 포함된 경우만 분석 대상

#### 1.3 빈 파일 제외
- 파일 내용이 비어있거나 공백만 있는 경우 제외

#### 1.4 파일 크기 제한
- **High Priority 패턴 파일**: 최대 1000줄까지 읽습니다
  - 패턴: `main`, `app`, `index`, `server`, `client`, `config`, `settings`, `router`, `controller`, `service`, `manager`, `handler`, `api`
- **일반 파일**: 최대 500줄까지만 읽습니다 (토큰 제한 방지)
- 각 파일은 설정된 줄 수를 초과하면 앞부분만 사용

### 2단계: 중요도 점수 계산 (`_calculate_file_score`)

각 파일에 대해 중요도 점수를 계산하여 우선순위를 결정합니다.

#### 2.1 파일명 패턴 점수 (가장 중요)

**High Priority 패턴** (+100점):
- `main`, `app`, `index`, `server`, `client`
- `config`, `settings`, `router`, `controller`
- `service`, `manager`, `handler`, `api`

**Medium Priority 패턴** (+50점):
- `model`, `view`, `component`, `module`

**Low Priority 패턴** (-30점, 페널티):
- `util`, `helper`, `common`, `test`, `spec`

**로직**:
```python
filename = file_path.name.lower()  # 소문자 변환
# High priority 패턴이 있으면 +100점
# Medium priority 패턴이 있으면 +50점
# Low priority 패턴이 있으면 -30점
```

#### 2.2 경로 깊이 점수

**로직**:
```python
depth = len(file_path.relative_to(self.project_path).parts)
score += max(0, 50 - (depth * 10))
```

**점수 계산**:
- 루트 디렉토리 (depth=1): +50점
- 1단계 하위 (depth=2): +40점
- 2단계 하위 (depth=3): +30점
- 3단계 하위 (depth=4): +20점
- 4단계 하위 (depth=5): +10점
- 5단계 이상 (depth≥6): +0점

**의도**: 프로젝트 루트에 가까운 파일일수록 중요도가 높다고 판단

#### 2.3 복잡도 분석 점수

**함수/메서드 개수** (+5점/개):
```python
func_patterns = [
    r'def\s+\w+',              # Python
    r'function\s+\w+',          # JavaScript
    r'func\s+\w+',              # Go/Swift
    r'public\s+\w+\s+\w+\s*\(', # Java/C#
]
func_count = sum(len(re.findall(pattern, content)) for pattern in func_patterns)
score += func_count * 5
```

**클래스 개수** (+10점/개):
```python
class_patterns = [
    r'class\s+\w+',      # Python/Java/C#/JavaScript
    r'struct\s+\w+',     # Go/Rust
    r'interface\s+\w+',  # TypeScript/Java
]
class_count = sum(len(re.findall(pattern, content)) for pattern in class_patterns)
score += class_count * 10
```

**Import 개수** (+3점/개):
```python
import_patterns = [
    r'import\s+',              # Python/JavaScript/Java
    r'from\s+\w+\s+import',    # Python
    r'require\(',              # JavaScript
    r'use\s+',                 # Rust/PHP
]
import_count = sum(len(re.findall(pattern, content)) for pattern in import_patterns)
score += import_count * 3
```

**의도**: 
- 함수/클래스가 많을수록 복잡하고 중요
- Import가 많을수록 다른 모듈과의 연결이 많고 중요

#### 2.4 파일 크기 점수

**High Priority 패턴 파일**:
```python
if 50 <= line_count <= 1000:
    score += 20      # 적절한 크기 (1000줄까지)
elif line_count > 1000:
    score += 10      # 너무 큰 파일 (페널티)
```

**일반 파일**:
```python
if 50 <= line_count <= 500:
    score += 20      # 적절한 크기
elif line_count > 500:
    score += 10      # 너무 큰 파일 (페널티)
# 50줄 미만은 점수 없음
```

**의도**:
- High Priority 파일: 50-1000줄 범위가 적절 (더 많은 코드 분석)
- 일반 파일: 50-500줄 범위가 적절
- 각 범위 초과: 너무 커서 분석이 어려움 (낮은 점수)
- 50줄 미만: 너무 작아서 중요도 낮음

### 3단계: 파일 선택 및 정렬

#### 3.1 점수 기반 정렬
```python
file_scores.sort(key=lambda x: x['score'], reverse=True)
```

**로직**: 점수가 높은 순서대로 정렬

#### 3.2 상위 N개 선택
```python
selected_files = file_scores[:max_files]  # 기본값: 50개
```

**기본값**: 최대 50개 파일 선택

## 점수 계산 예시

### 예시 1: `src/main.py` (200줄, 함수 10개, 클래스 2개, import 5개)

```
파일명 패턴: 'main' → +100점 (High Priority)
경로 깊이: depth=2 → +40점
함수 개수: 10개 → +50점 (10 × 5)
클래스 개수: 2개 → +20점 (2 × 10)
Import 개수: 5개 → +15점 (5 × 3)
파일 크기: 200줄 → +20점 (50-500 범위)

총점: 245점
```

### 예시 2: `src/utils/helper.py` (100줄, 함수 5개, import 3개)

```
파일명 패턴: 'helper' → -30점 (Low Priority, 페널티)
경로 깊이: depth=3 → +30점
함수 개수: 5개 → +25점 (5 × 5)
클래스 개수: 0개 → +0점
Import 개수: 3개 → +9점 (3 × 3)
파일 크기: 100줄 → +20점 (50-500 범위)

총점: 54점
```

### 예시 3: `tests/test_sample.py` (50줄, 함수 3개)

```
파일명 패턴: 'test' → -30점 (Low Priority, 페널티)
경로 깊이: depth=2 → +40점
함수 개수: 3개 → +15점 (3 × 5)
클래스 개수: 0개 → +0점
Import 개수: 2개 → +6점 (2 × 3)
파일 크기: 50줄 → +20점 (50-500 범위)

총점: 51점
```

## 선택 로직의 특징

### 장점
1. **스마트 선정**: 단순 파일명이 아닌 복합적 기준으로 중요도 판단
2. **토큰 효율성**: 최대 50개 파일만 선택하여 API 비용 절감
3. **프로젝트 구조 고려**: 루트에 가까운 파일 우선
4. **복잡도 반영**: 함수/클래스가 많은 파일 우선

### 한계점
1. **고정된 패턴**: 파일명 패턴이 하드코딩되어 있어 커스터마이징 어려움
2. **언어별 차이 미반영**: 언어별 특성을 고려하지 않음
3. **최대 파일 수 제한**: 50개로 제한되어 대규모 프로젝트에서 일부 파일 누락 가능
4. **파일 크기 제한**: 
   - High Priority 파일: 1000줄까지만 읽어서 매우 큰 파일의 뒷부분 분석 불가
   - 일반 파일: 500줄까지만 읽어서 큰 파일의 뒷부분 분석 불가

## 개선 제안

1. **설정 파일 지원**: 파일명 패턴을 설정 파일로 관리
2. **언어별 가중치**: 언어별로 다른 점수 가중치 적용
3. **동적 파일 수 조정**: 프로젝트 크기에 따라 선택 파일 수 조정
4. **청크 분할**: 큰 파일을 여러 청크로 나누어 분석

## 관련 코드 위치

- **파일 선정 로직**: `src/analyzers/ai_analyzer.py::_collect_code_samples()`
- **점수 계산 로직**: `src/analyzers/ai_analyzer.py::_calculate_file_score()`
- **호출 위치**: `src/analyzers/ai_analyzer.py::analyze()`


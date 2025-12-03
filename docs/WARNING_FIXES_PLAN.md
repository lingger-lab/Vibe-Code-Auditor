# 경고 이슈 개선 계획

## 📊 경고 통계 (총 220개)

### 주요 경고 유형별 분류

1. **Use lazy % formatting in logging functions** (~120개)
   - 로깅 함수에서 f-string 대신 % 포맷팅 사용 권장
   - 성능 및 메모리 효율성 향상

2. **Catching too general exception Exception** (~30개)
   - 너무 일반적인 Exception 대신 구체적인 예외 타입 지정
   - 디버깅 및 에러 처리 개선

3. **Unused import** (~15개)
   - 사용하지 않는 import 제거
   - 코드 정리 및 가독성 향상

4. **Unused variable** (~10개)
   - 사용하지 않는 변수 제거 또는 사용
   - 메모리 효율성 향상

5. **Access to a protected member** (~20개)
   - 테스트 파일에서 protected 멤버 접근
   - 테스트 코드이므로 pylint 무시 주석 추가

6. **기타 경고** (~25개)
   - Redefining name from outer scope
   - Unnecessary pass statement
   - Using an f-string that does not have any interpolated variables
   - No exception type(s) specified

## 🎯 개선 우선순위

### 1단계: 핵심 파일 수정 (즉시 적용)
- `vibe_auditor.py` - 사용하지 않는 import 제거, Exception 구체화
- `src/analyzers/ai_analyzer.py` - 로깅 포맷팅, Exception 구체화
- `src/analyzers/static_analyzer.py` - 로깅 포맷팅, Exception 구체화
- `src/cli/main.py` - 로깅 포맷팅, Exception 구체화, 사용하지 않는 변수

### 2단계: 유틸리티 파일 수정
- `src/utils/` 디렉토리 내 파일들
- `src/config/` 디렉토리 내 파일들
- `src/reporters/` 디렉토리 내 파일들

### 3단계: 테스트 파일 수정
- 테스트 파일의 protected 멤버 접근에 pylint 무시 주석 추가
- 사용하지 않는 import 제거

### 4단계: 예제 파일 수정 (선택적)
- `examples/` 디렉토리 내 파일들은 예제이므로 선택적 수정

## 📝 수정 가이드

### 로깅 lazy % 포맷팅

**변경 전:**
```python
logger.debug(f"AI response length: {len(response_text)} characters")
logger.info(f"Selected {len(selected_files)} files")
```

**변경 후:**
```python
logger.debug("AI response length: %d characters", len(response_text))
logger.info("Selected %d files", len(selected_files))
```

### Exception 구체화

**변경 전:**
```python
except Exception as e:
    logger.error(f"Error: {e}")
```

**변경 후:**
```python
except (ValueError, IOError, OSError) as e:
    logger.error("Error: %s", e)
except Exception as e:  # pylint: disable=broad-except
    logger.error("Unexpected error: %s", e, exc_info=True)
```

### 사용하지 않는 import 제거

**변경 전:**
```python
import os
import subprocess
from pathlib import Path
```

**변경 후:**
```python
from pathlib import Path
# os, subprocess 제거 (사용하지 않음)
```

## ✅ 완료 기준

- 핵심 파일들의 주요 경고 80% 이상 해결
- 로깅 포맷팅 경고 90% 이상 해결
- Exception 처리 경고 70% 이상 구체화
- 사용하지 않는 import/변수 100% 제거



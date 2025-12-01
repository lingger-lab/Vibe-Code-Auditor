# 예제 프로젝트

이 디렉토리에는 Vibe-Code Auditor를 테스트할 수 있는 샘플 프로젝트가 포함되어 있습니다.

## sample-project

의도적으로 다양한 유형의 이슈를 포함한 Python 프로젝트입니다.

### 포함된 이슈

1. **Critical (치명적)**
   - 하드코딩된 비밀번호 (`DATABASE_PASSWORD`, `API_KEY`)
   - SQL Injection 취약점 (`get_user_data` 함수)

2. **Warning (경고)**
   - 코드 중복 (`calculate_total_price` vs `calculate_total_cost`)
   - 높은 복잡도 (`process_order` 함수 - 중첩된 if문)

3. **Info (정보)**
   - 불명확한 변수명 (`calc` 함수의 `a`, `b`, `c`, `x`, `y`, `z`)
   - 개선 가능한 로직 구조

### 테스트 방법

```bash
# 배포 관점으로 분석
vibe-auditor --path examples/sample-project --mode deployment

# 자가 사용 관점으로 분석
vibe-auditor --path examples/sample-project --mode personal

# AI 분석 없이 정적 분석만
vibe-auditor --path examples/sample-project --mode deployment --skip-ai
```

### 예상 결과

**배포 관점 (deployment):**
- Critical: 2-3개 (보안 이슈 위주)
- Warning: 3-5개 (성능/구조 이슈)
- Info: 2-4개 (개선 제안)

**자가 사용 관점 (personal):**
- Critical: 1-2개
- Warning: 4-6개 (중복 코드, 복잡도 위주)
- Info: 5-10개 (가독성, 스타일 개선)

## 자신의 프로젝트 테스트

이 예제로 도구가 잘 작동하는지 확인한 후, 자신의 프로젝트에 적용해보세요!

```bash
vibe-auditor --path /path/to/your/project --mode deployment
```

# 사용 가이드

## 기본 사용법

### 1. 배포 관점 분석

프로젝트를 배포하기 전에 보안, 성능, 확장성을 중점적으로 검사합니다.

```bash
vibe-auditor --path /path/to/your/project --mode deployment
```

**체크 항목:**
- 🔒 보안 취약점 (SQL Injection, XSS, CSRF 등)
- ⚡ 성능 이슈 (복잡도, 비효율적 알고리즘)
- 📈 확장성 (하드코딩된 값, 설정 관리)
- 🔄 CI/CD 호환성

**적용 도구:**
- Semgrep (보안 스캔)
- Pylint (코드 품질)
- Claude AI (주관적 리뷰)

### 2. 자가 사용 관점 분석

개인 프로젝트나 학습용 코드의 가독성과 유지보수성을 검사합니다.

```bash
vibe-auditor --path /path/to/your/project --mode personal
```

**체크 항목:**
- 📖 코드 가독성 (변수명, 함수명, 주석)
- ♻️ 코드 중복 (DRY 원칙 위배)
- 🧹 유지보수성 (복잡도, 구조)
- 📝 문서화 상태

**적용 도구:**
- jscpd (중복 감지)
- Pylint (스타일 검사)
- Claude AI (개선 제안)

### 3. 정적 분석만 실행

AI 분석을 건너뛰고 정적 분석 도구만 사용합니다.

```bash
vibe-auditor --path /path/to/your/project --mode deployment --skip-ai
```

**사용 시나리오:**
- API 키가 없는 경우
- 빠른 검증이 필요한 경우
- 오프라인 환경

## 실전 예제

### 예제 1: Python 프로젝트 분석

```bash
# Django 프로젝트 배포 전 검사
vibe-auditor --path ~/projects/my-django-app --mode deployment

# Flask API 보안 검증
vibe-auditor --path ~/projects/flask-api --mode deployment

# 개인 Python 스크립트 개선
vibe-auditor --path ~/scripts/automation --mode personal
```

### 예제 2: JavaScript 프로젝트 분석

```bash
# React 앱 배포 전 검사
vibe-auditor --path ~/projects/react-app --mode deployment

# Node.js API 성능 검증
vibe-auditor --path ~/projects/nodejs-api --mode deployment

# 개인 JS 프로젝트 리팩토링
vibe-auditor --path ~/learning/js-tutorial --mode personal
```

### 예제 3: 혼합 언어 프로젝트

```bash
# Full-stack 프로젝트 (Python + React)
vibe-auditor --path ~/projects/fullstack-app --mode deployment
```

## 리포트 해석

### 심각도 레벨

#### 🔴 Critical (치명적)
- **즉시 조치 필요**
- 보안 취약점, 데이터 손실 위험, 치명적 버그
- 예: SQL Injection, 하드코딩된 비밀번호, 메모리 누수

#### 🟡 Warning (경고)
- **배포 전 검토 권장**
- 성능 이슈, 코드 중복, 복잡도 초과
- 예: 15% 이상 코드 중복, 복잡도 10 초과 함수

#### 🟢 Info (정보)
- **개선 제안**
- 리팩토링 방향, 스타일 개선, 문서화
- 예: 변수명 개선, 주석 추가, 타입 힌트 추가

### 리포트 섹션

1. **분석 요약**: 발견된 이슈의 개수와 심각도별 분류
2. **정적 분석 결과**: 자동화 도구가 발견한 구체적 이슈
3. **AI 코드 리뷰**: Claude가 제안하는 주관적 개선사항
4. **권장 사항**: 관점별 맞춤 액션 아이템

## 워크플로우 통합

### 1. Git Pre-commit Hook

`.git/hooks/pre-commit` 파일 생성:

```bash
#!/bin/bash
echo "Running Vibe-Code Auditor..."
vibe-auditor --path . --mode deployment --skip-ai

if [ $? -ne 0 ]; then
    echo "Code quality check failed. Please fix issues before committing."
    exit 1
fi
```

### 2. CI/CD 파이프라인 통합

**GitHub Actions 예제** (`.github/workflows/code-audit.yml`):

```yaml
name: Code Audit

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install Vibe-Code Auditor
        run: |
          pip install -r requirements.txt
          pip install -e .
      - name: Run Analysis
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          vibe-auditor --path . --mode deployment
```

### 3. VS Code Task

`.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Vibe Audit: Deployment",
      "type": "shell",
      "command": "vibe-auditor --path ${workspaceFolder} --mode deployment",
      "problemMatcher": []
    },
    {
      "label": "Vibe Audit: Personal",
      "type": "shell",
      "command": "vibe-auditor --path ${workspaceFolder} --mode personal",
      "problemMatcher": []
    }
  ]
}
```

## 팁과 모범 사례

### 1. 정기적 분석
- 주 1회: 개인 프로젝트 가독성 검사
- 배포 전: 항상 deployment 모드 실행
- PR 전: 변경 사항 검증

### 2. 이슈 우선순위
1. Critical 이슈 → 즉시 수정
2. Warning 이슈 → 배포 전 검토
3. Info 이슈 → 시간 날 때 개선

### 3. AI 분석 활용
- 복잡한 로직: AI의 아키텍처 제안 참고
- 네이밍: AI의 변수/함수명 제안 검토
- 리팩토링: AI의 구조 개선 아이디어 활용

### 4. 정적 분석 도구 조합
- Python: Pylint + Semgrep
- JavaScript: ESLint + Semgrep
- 모든 프로젝트: jscpd로 중복 체크

## 문제 해결

### Q: 분석이 너무 오래 걸립니다
A: `--skip-ai` 플래그를 사용하거나, 분석 대상 파일을 제한하세요.

### Q: 너무 많은 Info 이슈가 표시됩니다
A: deployment 모드는 Critical/Warning 위주로, personal 모드는 전체를 확인하세요.

### Q: False positive가 많습니다
A: AI 분석 결과는 제안사항이므로, 프로젝트 컨텍스트에 맞게 판단하세요.

### Q: 특정 파일/폴더를 제외하고 싶습니다
A: `.env` 파일에서 `EXCLUDE_PATTERNS` 설정을 추가하세요.

```
EXCLUDE_PATTERNS=node_modules,venv,test_data,migrations
```

## 다음 단계

1. 첫 분석 실행하기
2. Critical 이슈 해결하기
3. CI/CD에 통합하기
4. 팀과 결과 공유하기
5. 정기 분석 습관화하기

---

더 많은 정보는 [README.md](README.md)와 [설치 가이드](INSTALL.md)를 참고하세요.

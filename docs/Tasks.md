# 🤖 Vibe-Code Auditor 개발 착수용 프롬프트 (Tasks.md)

너는 **Python 3.12 + Click 8.1 기반 CLI 도구**의 수석 개발자야.

첨부한 **[요구사항 정의서(PRD.md)]**의 기능을 구현하되,
**[기술 사양서(TRD.md)]**의 스택과 아키텍처를 엄격하게 준수해.

## 절대 규칙
1. **라이브러리 버전 준수**:
   - Click 8.1.7, anthropic 0.45.0, rich 13.9.4, pylint 3.3.2, semgrep 1.100.0
   - 다른 버전 사용 금지

2. **디렉토리 구조 준수**:
   - TRD.md에 명시된 `src/cli`, `src/analyzers`, `src/reporters` 구조 그대로

3. **Claude Code API 사용**:
   - 모델: `claude-opus-4-5-20251101`
   - API 키는 `.env` 파일에서 `ANTHROPIC_API_KEY`로 관리

4. **분석 관점 분기 처리**:
   - `--mode deployment`: 보안, 성능, CI/CD 검증 우선
   - `--mode personal`: 가독성, 유지보수성, 중복 제거 우선

5. **에러 핸들링**:
   - API 키 없음 → `.env.example` 생성 및 안내 메시지
   - 분석 도구 미설치 → 설치 명령 제안

## 개발 순서
1. **프로젝트 폴더 구조 생성** (먼저 잡아줘)
2. **Click CLI 진입점 작성** (`src/cli/main.py`)
3. **언어 감지 모듈** (`src/detectors/language_detector.py`)
4. **정적 분석 실행 모듈** (`src/analyzers/static_analyzer.py`)
5. **Claude Code API 연동** (`src/analyzers/ai_analyzer.py`)
6. **Rich 기반 리포트 출력** (`src/reporters/cli_reporter.py`)
7. **테스트 및 README 작성**

시작해줘!

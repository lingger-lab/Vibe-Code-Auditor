# ⚙️ [Vibe-Code Auditor] 기술 사양서 (TRD.md)

## 권장 스택
- **언어**: Python 3.12+
- **CLI 프레임워크**: Click 8.1+ (간결하고 확장 가능한 명령 구조)
- **AI 분석**: Claude Code API (Anthropic) - `claude-opus-4-5-20251101`
- **정적 분석 도구**:
  - Pylint 3.x (Python)
  - ESLint 9.x (JavaScript/TypeScript)
  - Semgrep 1.x (다중 언어 보안 스캔)
  - jscpd 4.x (코드 중복 감지)
- **출력 포맷팅**: Rich 13.x (터미널 색상 및 테이블 출력)
- **환경 관리**: python-dotenv (API 키 관리)

## 선정 이유
1. **Python 3.12 + Click**:
   - AI 협업 시 가장 생산성 높은 언어
   - Click은 argparse보다 확장성/가독성 우수 ([Python CLI Best Practices 2025](https://www.pythonsnacks.com/p/click-vs-argparse-python))

2. **Claude Code API**:
   - 2025년 기준 가장 강력한 코드 리뷰 AI ([Anthropic Claude Code](https://www.anthropic.com/news/automate-security-reviews-with-claude-code))
   - `/security-review` 명령으로 보안 취약점 탐지 특화

3. **혼합 정적 분석**:
   - SonarQube, ESLint, Pylint, Semgrep 조합이 2025년 표준 ([Static Analysis Tools 2025](https://www.qodo.ai/blog/best-static-code-analysis-tools/))
   - jscpd로 언어 무관 중복 코드 감지 ([jscpd npm](https://www.npmjs.com/package/jscpd))

## 핵심 아키텍처 & 스타일 가이드

### 디렉토리 구조 (권장)
```
vibe-auditor/
├── src/
│   ├── cli/
│   │   └── main.py           # Click 기반 CLI 진입점
│   ├── analyzers/
│   │   ├── ai_analyzer.py    # Claude Code API 호출
│   │   ├── static_analyzer.py # 정적 분석 도구 실행
│   │   └── duplication.py    # jscpd 중복 감지
│   ├── detectors/
│   │   └── language_detector.py # 프로젝트 언어 자동 감지
│   ├── reporters/
│   │   └── cli_reporter.py   # Rich 기반 터미널 출력
│   └── config/
│       └── settings.py       # 분석 규칙 및 우선순위 설정
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

### 필수 라이브러리 목록 (requirements.txt)
```
click==8.1.7
anthropic==0.45.0
rich==13.9.4
python-dotenv==1.0.1
pylint==3.3.2
semgrep==1.100.0
```

### AI 코딩 주의사항
1. **Click 명령 구조**:
   - `@click.command()` 데코레이터 활용
   - `--path`, `--mode` 옵션으로 경로 및 분석 관점 전달

2. **Claude Code API 호출**:
   - Anthropic SDK 사용: `anthropic.Anthropic(api_key=...)`
   - 프롬프트 예시:
     ```
     "다음 프로젝트를 {mode} 관점에서 분석하고,
      보안/성능/가독성 이슈를 우선순위별로 정리해줘"
     ```

3. **정적 분석 도구 실행**:
   - subprocess로 각 도구 CLI 호출 (예: `subprocess.run(['pylint', path])`)
   - 언어 감지 후 해당 도구만 선택 실행

4. **에러 핸들링**:
   - API 키 없을 시 명확한 에러 메시지 + `.env.example` 안내
   - 분석 도구 미설치 시 자동 설치 제안 (`pip install pylint` 등)

5. **출력 포맷**:
   - Rich 라이브러리의 `Console`, `Table`, `Syntax` 활용
   - 배포 관점 → 보안 우선, 자가 사용 관점 → 가독성 우선 정렬

## 참고 자료
- [13 Best Static Code Analysis Tools For 2025 - Qodo](https://www.qodo.ai/blog/best-static-code-analysis-tools/)
- [Automate security reviews with Claude Code | Anthropic](https://www.anthropic.com/news/automate-security-reviews-with-claude-code)
- [GitHub - anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)
- [Click vs argparse - Python CLI Best Practices](https://www.pythonsnacks.com/p/click-vs-argparse-python)
- [5 Best Duplicate Code Checker Tools for Developers in 2025](https://www.codeant.ai/blogs/best-duplicate-code-checker-tools)
- [jscpd - npm](https://www.npmjs.com/package/jscpd)
- [Finding duplicated code with CPD | PMD Source Code Analyzer](https://pmd.github.io/pmd/pmd_userdocs_cpd.html)
- [Static Analysis Tools Every Developer Should Know in 2025](https://toxigon.com/static-analysis-tools-every-developer-should-know)

"""AI-powered code analysis using Claude Code API."""

import re
from pathlib import Path
from typing import Dict, Any, List, Set
import anthropic

from src.config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL, ANALYSIS_MODES
from src.utils.logger import setup_logger

# Module logger
logger = setup_logger(__name__)

# Claude API 기본 타임아웃(초) - 테스트에서도 동일 상수를 사용해 검증
DEFAULT_CLAUDE_TIMEOUT = 180.0


class AIAnalyzer:
    """Performs AI-based code review using Claude Code API."""

    def __init__(self, project_path: Path, mode: str):
        """
        Initialize the AI analyzer.

        Args:
            project_path: Path to the project directory
            mode: Analysis mode ('deployment' or 'personal')
        """
        self.project_path = project_path
        self.mode = mode
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.mode_config = ANALYSIS_MODES[mode]
        self.analyzed_files: Set[str] = set()  # Track analyzed files to avoid duplicates
        
        # High Priority 패턴 파일 목록 (1000줄까지 분석)
        self.high_priority_patterns = [
            'main', 'app', 'index', 'server', 'client',
            'config', 'settings', 'router', 'controller',
            'service', 'manager', 'handler', 'api'
        ]

    def _calculate_file_score(self, file_path: Path, content: str) -> float:
        """
        파일의 중요도 점수를 계산합니다.
        
        점수 계산 기준:
        1. 파일명 패턴: High(+100), Medium(+50), Low(-30)
        2. 경로 깊이: 루트에 가까울수록 높은 점수 (최대 +50)
        3. 복잡도: 함수(+5/개), 클래스(+10/개), import(+3/개)
        4. 파일 크기: 
           - High Priority: 50-1000줄(+20), 1000줄 초과(+10)
           - 일반 파일: 50-500줄(+20), 500줄 초과(+10)
        
        상세 점수 계산 로직은 docs/FILE_SELECTION_LOGIC.md 참조

        Args:
            file_path: 파일 경로
            content: 파일 내용

        Returns:
            중요도 점수 (높을수록 중요)
        """
        score = 0.0
        filename = file_path.name.lower()

        # 1. Filename pattern scoring (most important)
        # High Priority 패턴은 인스턴스 변수에서 가져옴 (1000줄까지 분석)
        high_priority_patterns = self.high_priority_patterns
        medium_priority_patterns = ['model', 'view', 'component', 'module']
        low_priority_patterns = ['util', 'helper', 'common', 'test', 'spec']

        for pattern in high_priority_patterns:
            if pattern in filename:
                score += 100
                break
        for pattern in medium_priority_patterns:
            if pattern in filename:
                score += 50
                break
        for pattern in low_priority_patterns:
            if pattern in filename:
                score -= 30  # Penalty for utility files

        # 2. Path depth (prefer files closer to root)
        depth = len(file_path.relative_to(self.project_path).parts)
        score += max(0, 50 - (depth * 10))  # Closer to root = higher score

        # 3. Complexity analysis
        lines = content.split('\n')

        # Count functions/methods
        func_patterns = [
            r'def\s+\w+',  # Python
            r'function\s+\w+',  # JavaScript
            r'func\s+\w+',  # Go/Swift
            r'public\s+\w+\s+\w+\s*\(',  # Java/C#
        ]
        func_count = sum(len(re.findall(pattern, content)) for pattern in func_patterns)
        score += func_count * 5

        # Count classes
        class_patterns = [
            r'class\s+\w+',  # Python/Java/C#/JavaScript
            r'struct\s+\w+',  # Go/Rust
            r'interface\s+\w+',  # TypeScript/Java
        ]
        class_count = sum(len(re.findall(pattern, content)) for pattern in class_patterns)
        score += class_count * 10

        # Count imports (indicates connections to other modules)
        import_patterns = [
            r'import\s+',  # Python/JavaScript/Java
            r'from\s+\w+\s+import',  # Python
            r'require\(',  # JavaScript
            r'use\s+',  # Rust/PHP
        ]
        import_count = sum(len(re.findall(pattern, content)) for pattern in import_patterns)
        score += import_count * 3

        # 4. File size (larger files often more important, but not too large)
        line_count = len(lines)
        # High Priority 파일은 1000줄까지 읽으므로 점수 계산 기준 조정
        filename_lower = file_path.name.lower()
        is_high_priority = any(pattern in filename_lower for pattern in self.high_priority_patterns)
        
        if is_high_priority:
            # High Priority 파일: 50-1000줄 범위가 최적
            if 50 <= line_count <= 1000:
                score += 20
            elif line_count > 1000:
                score += 10
        else:
            # 일반 파일: 50-500줄 범위가 최적
            if 50 <= line_count <= 500:
                score += 20
            elif line_count > 500:
                score += 10

        return score

    def _collect_code_samples(self, max_files: int = 50, skip_analyzed: bool = True) -> List[Dict[str, str]]:
        """
        프로젝트에서 스마트하게 선정된 코드 샘플을 수집합니다.
        
        중요도 점수 기반으로 파일을 선정하며, 다음 기준을 사용합니다:
        1. 파일명 패턴 (main.py, app.js 등 핵심 파일 우선)
        2. 경로 깊이 (루트에 가까운 파일 우선)
        3. 복잡도 분석 (함수, 클래스, import 개수)
        4. 파일 크기 (High Priority: 50-1000줄, 일반: 50-500줄)
        
        **High Priority 패턴 파일** (1000줄까지 분석):
        - main, app, index, server, client, config, settings, router, 
          controller, service, manager, handler, api
        
        상세한 선정 로직은 docs/FILE_SELECTION_LOGIC.md 참조

        Args:
            max_files: 최대 선택 파일 수 (기본값: 50개)
            skip_analyzed: 이미 분석한 파일 건너뛰기 여부

        Returns:
            중요도 순으로 정렬된 코드 샘플 리스트
        """
        exclude_dirs = {'node_modules', 'venv', '.venv', '.git', '__pycache__', 'build', 'dist', 'target', 'vendor'}
        file_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx',  # Python, JavaScript, TypeScript
            '.go',  # Go
            '.rs',  # Rust
            '.java', '.kt', '.kts',  # Java, Kotlin
            '.php',  # PHP
            '.cs',  # C#
            '.rb',  # Ruby
            '.swift'  # Swift
        }

        # Collect all eligible files with scores
        file_scores = []

        for file_path in self.project_path.rglob('*'):
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue

            # Only include relevant code files
            if not (file_path.is_file() and file_path.suffix in file_extensions):
                continue

            # Skip already analyzed files if requested
            relative_path = str(file_path.relative_to(self.project_path))
            if skip_analyzed and relative_path in self.analyzed_files:
                continue

            try:
                # High Priority 패턴 파일은 1000줄, 일반 파일은 500줄까지 읽기
                filename_lower = file_path.name.lower()
                is_high_priority = any(pattern in filename_lower for pattern in self.high_priority_patterns)
                max_lines = 1000 if is_high_priority else 500
                
                # Read file content (High Priority는 1000줄, 일반은 500줄로 제한)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[:max_lines]
                    content = ''.join(lines)
                    
                if is_high_priority:
                    logger.debug("High Priority file detected: %s (reading %d lines)", relative_path, len(lines))

                if not content.strip():  # Skip empty files
                    continue

                # Calculate importance score
                score = self._calculate_file_score(file_path, content)

                file_scores.append({
                    'path': relative_path,
                    'full_path': file_path,
                    'content': content,
                    'extension': file_path.suffix,
                    'score': score
                })

            except (IOError, OSError, UnicodeDecodeError) as e:
                logger.debug("Failed to read %s: %s", file_path, e)
                continue

        # Sort by score (descending) and take top N
        file_scores.sort(key=lambda x: x['score'], reverse=True)
        selected_files = file_scores[:max_files]

        logger.info("Selected %d files from %d candidates", len(selected_files), len(file_scores))
        if selected_files:
            logger.info("Top file: %s (score: %.1f)", selected_files[0]['path'], selected_files[0]['score'])

        # Mark files as analyzed
        for file_info in selected_files:
            self.analyzed_files.add(file_info['path'])

        # Return samples without score (for API call)
        return [{
            'path': f['path'],
            'content': f['content'],
            'extension': f['extension']
        } for f in selected_files]

    def _build_analysis_prompt(self, code_samples: List[Dict[str, str]]) -> str:
        """
        Build optimized prompt for Claude Code API with mode-specific instructions.

        Args:
            code_samples: List of code samples to analyze

        Returns:
            Formatted prompt string
        """
        mode_name = self.mode_config['name']
        priorities = ', '.join(self.mode_config['priorities'])
        description = self.mode_config['description']

        # Build code context with file information
        code_context = ""
        file_count = len(code_samples)
        for idx, sample in enumerate(code_samples[:20], 1):  # 최대 20개 파일만 포함
            code_context += f"\n\n### File {idx}/{file_count}: {sample['path']}\n```{sample['extension'][1:]}\n{sample['content'][:2000]}\n```"

        # 모드별 구체적인 분석 체크리스트 생성
        if self.mode == 'deployment':
            analysis_checklist = """
**🔴 Critical (치명적) - 즉시 수정 필요:**
1. 보안 취약점:
   - SQL Injection, XSS, CSRF 취약점
   - 하드코딩된 비밀번호/API 키
   - 인증/인가 로직 누락
   - 암호화되지 않은 민감 정보 전송
   - 파일 업로드 검증 부족
   - 경로 조작 취약점 (Path Traversal)
   
2. 치명적 버그:
   - Null 포인터 역참조 가능성
   - 메모리 누수
   - 무한 루프/재귀
   - 예외 처리 누락으로 인한 크래시
   - 데이터 손실 위험 (트랜잭션 미사용 등)

**🟡 Warning (경고) - 배포 전 수정 권장:**
1. 성능 이슈:
   - N+1 쿼리 문제
   - 비효율적인 알고리즘 (O(n²) 이상)
   - 불필요한 반복문/재귀
   - 대용량 데이터 처리 시 메모리 부족 가능성
   - 캐싱 미적용으로 인한 성능 저하
   
2. 확장성 문제:
   - 하드코딩된 리소스 제한
   - 단일 스레드 병목
   - 상태 저장으로 인한 확장 불가
   - 분산 환경 비호환 코드
   
3. CI/CD 문제:
   - 테스트 커버리지 부족
   - 빌드/배포 스크립트 오류 가능성
   - 환경 변수 관리 부실
   - 로깅/모니터링 부재"""
        else:  # personal mode
            analysis_checklist = """
**🔴 Critical (치명적) - 즉시 수정 필요:**
1. 코드 품질 문제:
   - 복잡도가 과도한 함수/메서드 (순환 복잡도 > 15)
   - 중복 코드 블록 (DRY 원칙 위반)
   - 매직 넘버/문자열 하드코딩
   - 전역 변수 남용
   
2. 유지보수성 문제:
   - 명확하지 않은 변수/함수명
   - 주석 부족 또는 오래된 주석
   - 책임이 불명확한 클래스/모듈
   - 의존성 과다 결합

**🟡 Warning (경고) - 개선 권장:**
1. 가독성 문제:
   - 긴 함수/메서드 (100줄 이상)
   - 깊은 중첩 구조 (4단계 이상)
   - 일관성 없는 코딩 스타일
   - 불필요한 복잡성
   
2. 중복 코드:
   - 동일한 로직 반복
   - 유사한 함수/메서드 다수
   - 복사-붙여넣기 코드
   
3. 설계 문제:
   - 단일 책임 원칙 위반
   - 개방-폐쇄 원칙 미준수
   - 인터페이스 분리 원칙 위반"""

        # 공통 Info 항목
        info_checklist = """
**🟢 Info (정보) - 개선 제안:**
1. 코드 스타일:
   - PEP 8 / 코딩 컨벤션 미준수
   - 타입 힌트 부족
   - 문서화 개선 필요
   
2. 리팩토링 제안:
   - 더 나은 패턴 적용 가능성
   - 라이브러리/프레임워크 활용 개선
   - 성능 최적화 여지
   - 테스트 가능성 향상"""

        prompt = f"""당신은 10년 이상 경력의 시니어 코드 리뷰어입니다. 다음 프로젝트를 "{mode_name}" 관점에서 철저히 분석해주세요.

## 📋 분석 컨텍스트

**분석 모드**: {mode_name}
**우선순위**: {priorities}
**설명**: {description}

**분석 대상**: 총 {file_count}개 파일 (주요 파일 {min(20, file_count)}개 샘플 제공)

## 📁 코드 샘플
{code_context}

## 🔍 분석 체크리스트

{analysis_checklist}

{info_checklist}

## 📝 응답 형식 (반드시 준수)

각 이슈는 다음 형식으로 작성해주세요:

**[Critical] 구체적이고 명확한 이슈 제목**
- 설명: 문제의 원인, 영향 범위, 발생 가능성 등을 구체적으로 설명
- 파일: 문제가 발생한 파일 경로 (예: src/api/auth.py:45)
- 위치: 구체적인 라인 번호 또는 함수/메서드명
- 제안: 구체적인 수정 방안과 예시 코드 (가능한 경우)

**[Warning] 구체적이고 명확한 이슈 제목**
- 설명: 문제의 원인, 영향 범위, 발생 가능성 등을 구체적으로 설명
- 파일: 문제가 발생한 파일 경로
- 위치: 구체적인 라인 번호 또는 함수/메서드명
- 제안: 구체적인 수정 방안과 예시 코드 (가능한 경우)

**[Info] 구체적이고 명확한 이슈 제목**
- 설명: 개선이 필요한 이유와 기대 효과
- 파일: 관련 파일 경로 (있는 경우)
- 제안: 구체적인 개선 방안

## ✅ 응답 요구사항

1. **최소 이슈 수**: 최소 5개 이상의 이슈를 찾아주세요. 코드가 완벽해 보여도 개선 가능한 부분을 찾아주세요.

2. **우선순위**: Critical → Warning → Info 순서로 정렬해주세요.

3. **구체성**: 
   - 모호한 표현 지양 ("코드가 복잡합니다" ❌)
   - 구체적인 지적 ("함수 calculate_total()이 200줄이며 15개 이상의 조건문을 포함합니다" ✅)

4. **실행 가능성**: 
   - 모든 제안은 실제로 구현 가능해야 합니다
   - 가능하면 예시 코드를 포함해주세요

5. **파일 경로**: 
   - 코드 샘플에 제공된 파일 경로를 정확히 사용해주세요
   - 여러 파일에 걸친 문제는 각각 명시해주세요

6. **형식 준수**: 
   - 반드시 **[Critical]**, **[Warning]**, **[Info]** 형식으로 시작
   - 각 항목은 `- 설명:`, `- 파일:`, `- 위치:`, `- 제안:` 형식으로 작성

## 🎯 분석 시 주의사항

- 제공된 코드 샘플을 기반으로 분석하되, 프로젝트 전체 구조를 고려해주세요
- 실제 운영 환경에서 발생할 수 있는 문제를 우선적으로 찾아주세요
- 이론적 문제보다는 실무에서 중요한 문제에 집중해주세요
- 각 이슈는 독립적으로 이해 가능해야 합니다

이제 분석을 시작해주세요."""

        return prompt

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Claude's response into structured data.
        다양한 응답 형식을 지원하도록 개선된 파싱 로직.

        Args:
            response_text: Raw response from Claude

        Returns:
            Structured analysis results
        """
        issues: List[Dict[str, Any]] = []
        current_severity = 'info'
        # 현재 파싱 중인 이슈 객체 (없을 때는 None)
        current_issue: Dict[str, Any] | None = None

        # 응답이 비어있는지 확인
        if not response_text or not response_text.strip():
            logger.warning("AI response is empty")
            return {
                'mode': self.mode,
                'raw_response': response_text,
                'issues': [],
                'summary': {
                    'total_issues': 0,
                    'by_severity': {'critical': 0, 'warning': 0, 'info': 0}
                }
            }

        # 응답 전체를 로그에 기록 (디버깅용)
        logger.debug("AI response length: %d characters", len(response_text))
        logger.debug("AI response preview (first 500 chars): %s", response_text[:500])

        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 다양한 심각도 마커 패턴 인식
            severity_patterns = {
                'critical': [
                    r'\*\*\[?Critical\]?',
                    r'\*\*Critical',
                    r'Critical:',
                    r'🔴',
                    r'\[Critical\]',
                    r'CRITICAL',
                    r'치명적',
                    r'긴급'
                ],
                'warning': [
                    r'\*\*\[?Warning\]?',
                    r'\*\*Warning',
                    r'Warning:',
                    r'🟡',
                    r'\[Warning\]',
                    r'WARNING',
                    r'경고'
                ],
                'info': [
                    r'\*\*\[?Info\]?',
                    r'\*\*Info',
                    r'Info:',
                    r'🟢',
                    r'\[Info\]',
                    r'INFO',
                    r'정보',
                    r'제안'
                ]
            }

            # 심각도 감지
            detected_severity = None
            for severity, patterns in severity_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        detected_severity = severity
                        break
                if detected_severity:
                    break

            if detected_severity:
                current_severity = detected_severity
                # 이전 이슈 저장
                if current_issue:
                    issues.append(current_issue)
                
                # 새 이슈 시작
                # 제목 추출 (심각도 마커 제거)
                title = line
                for pattern in severity_patterns[detected_severity]:
                    title = re.sub(pattern, '', title, flags=re.IGNORECASE)
                title = title.strip('*:[] ').strip()
                
                if not title:
                    # 다음 줄에서 제목 찾기
                    continue
                
                current_issue = {
                    'severity': detected_severity,
                    'title': title,
                    'details': []
                }
                logger.debug("Found %s issue: %s", detected_severity, title)
                
            elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                # 상세 정보 추가
                detail = line.lstrip('-•* ').strip()
                # current_issue가 딕셔너리인지 확인
                if current_issue and isinstance(current_issue, dict) and detail:
                    # details 키가 항상 리스트가 되도록 방어적 처리
                    details_list = current_issue.get('details')
                    if isinstance(details_list, list):
                        details_list.append(detail)
                    else:
                        # pylint가 item assignment를 싫어하므로 update로 대체
                        current_issue.update({'details': [detail]})
                elif not current_issue:
                    # 이슈 없이 상세 정보가 나온 경우, 기본 이슈 생성
                    current_issue = {
                        'severity': current_severity,
                        'title': '분석 결과',
                        'details': [detail]
                    }
            elif current_issue and isinstance(current_issue, dict):
                # 일반 텍스트를 상세 정보로 추가 (빈 줄이 아닌 경우)
                # current_issue가 딕셔너리인지 확인 후 접근
                if line and not line.startswith('#'):
                    details_list = current_issue.get('details')
                    if isinstance(details_list, list):
                        details_list.append(line)
                    else:
                        # pylint가 item assignment를 싫어하므로 update로 대체
                        current_issue.update({'details': [line]})

        # 마지막 이슈 추가
        if current_issue:
            issues.append(current_issue)

        # 파싱 결과 로깅
        logger.info("Parsed %d issues from AI response", len(issues))
        if issues:
            critical_count = sum(1 for i in issues if i['severity'] == 'critical')
            warning_count = sum(1 for i in issues if i['severity'] == 'warning')
            info_count = sum(1 for i in issues if i['severity'] == 'info')
            logger.debug("Issue breakdown: %d critical, %d warning, %d info", critical_count, warning_count, info_count)
        else:
            logger.warning("No issues parsed from AI response. Response might not match expected format.")
            logger.debug("Full response for debugging:\n%s", response_text)

        return {
            'mode': self.mode,
            'raw_response': response_text,
            'issues': issues,
            'summary': {
                'total_issues': len(issues),
                'by_severity': {
                    'critical': sum(1 for i in issues if i['severity'] == 'critical'),
                    'warning': sum(1 for i in issues if i['severity'] == 'warning'),
                    'info': sum(1 for i in issues if i['severity'] == 'info')
                }
            }
        }

    def analyze(self) -> Dict[str, Any]:
        """
        Perform AI-based code analysis.

        Returns:
            Dictionary containing AI analysis results
        """
        try:
            logger.info("Starting AI analysis for %s in %s mode", self.project_path, self.mode)

            # Collect code samples (smart selection: 50 most important files)
            code_samples = self._collect_code_samples(max_files=50, skip_analyzed=True)

            if not code_samples:
                logger.warning("No code files found to analyze in %s", self.project_path)
                return {
                    'mode': self.mode,
                    'error': 'No code files found to analyze',
                    'issues': [],
                    'summary': {'total_issues': 0, 'by_severity': {'critical': 0, 'warning': 0, 'info': 0}}
                }

            logger.info("Collected %d code samples for AI analysis", len(code_samples))

            # Build prompt
            prompt = self._build_analysis_prompt(code_samples)

            # Call Claude API with timeout and retry logic
            logger.info("Calling Claude API for code review...")
            message = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                # 네트워크 환경과 프로젝트 규모를 고려해 타임아웃을 여유 있게 설정
                # 기본값은 DEFAULT_CLAUDE_TIMEOUT (현재 180초)
                timeout=DEFAULT_CLAUDE_TIMEOUT
            )

            # Extract response text
            if not message.content or len(message.content) == 0:
                logger.error("Claude API returned empty response")
                return {
                    'mode': self.mode,
                    'error': 'Claude API returned empty response',
                    'issues': [],
                    'summary': {'total_issues': 0, 'by_severity': {'critical': 0, 'warning': 0, 'info': 0}}
                }
            
            response_text = message.content[0].text
            logger.info("Successfully received AI analysis response (%d characters)", len(response_text))

            # Parse and return results
            result = self._parse_ai_response(response_text)
            logger.info("AI analysis found %d issues", result['summary']['total_issues'])
            
            # 파싱된 이슈가 없으면 경고
            if result['summary']['total_issues'] == 0:
                logger.warning("AI analysis completed but no issues were parsed. "
                             "This might indicate a parsing issue or the code has no issues.")
                logger.debug("Raw response for review:\n%s...", response_text[:1000])
            
            return result

        except anthropic.APIConnectionError as e:
            logger.error("Claude API connection error: %s", e)
            return {
                'mode': self.mode,
                'error': f'Failed to connect to Claude API: {str(e)}. Check your internet connection.',
                'issues': [],
                'summary': {'total_issues': 0, 'by_severity': {'critical': 0, 'warning': 0, 'info': 0}}
            }
        except anthropic.RateLimitError as e:
            logger.error("Claude API rate limit exceeded: %s", e)
            return {
                'mode': self.mode,
                'error': f'API rate limit exceeded: {str(e)}. Please try again later.',
                'issues': [],
                'summary': {'total_issues': 0, 'by_severity': {'critical': 0, 'warning': 0, 'info': 0}}
            }
        except anthropic.AuthenticationError as e:
            logger.error("Claude API authentication error: %s", e)
            return {
                'mode': self.mode,
                'error': f'Authentication failed: {str(e)}. Check your ANTHROPIC_API_KEY.',
                'issues': [],
                'summary': {'total_issues': 0, 'by_severity': {'critical': 0, 'warning': 0, 'info': 0}}
            }
        except anthropic.APIError as e:
            logger.error("Claude API error: %s", e, exc_info=True)
            return {
                'mode': self.mode,
                'error': f'Claude API error: {str(e)}',
                'issues': [],
                'summary': {'total_issues': 0, 'by_severity': {'critical': 0, 'warning': 0, 'info': 0}}
            }
        except Exception as e:  # pylint: disable=broad-exception-caught
            # 예기치 못한 모든 예외에 대한 최후 방어선 (사용자에게는 명확한 에러 메시지 제공)
            logger.error("Unexpected error during AI analysis: %s", e, exc_info=True)
            return {
                'mode': self.mode,
                'error': f'AI analysis failed: {str(e)}',
                'issues': [],
                'summary': {'total_issues': 0, 'by_severity': {'critical': 0, 'warning': 0, 'info': 0}}
            }

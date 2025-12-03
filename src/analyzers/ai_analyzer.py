"""AI-powered code analysis using Claude Code API."""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import anthropic

from src.config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL, ANALYSIS_MODES
from src.utils.logger import setup_logger

# Module logger
logger = setup_logger(__name__)


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

    def _calculate_file_score(self, file_path: Path, content: str) -> float:
        """
        Calculate importance score for a file based on multiple criteria.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            Score (higher = more important)
        """
        score = 0.0
        filename = file_path.name.lower()

        # 1. Filename pattern scoring (most important)
        high_priority_patterns = [
            'main', 'app', 'index', 'server', 'client',
            'config', 'settings', 'router', 'controller',
            'service', 'manager', 'handler', 'api'
        ]
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
        if 50 <= line_count <= 500:
            score += 20
        elif line_count > 500:
            score += 10

        return score

    def _collect_code_samples(self, max_files: int = 50, skip_analyzed: bool = True) -> List[Dict[str, str]]:
        """
        Collect smart-selected code samples from the project.

        Uses intelligent ranking based on:
        1. Filename patterns (main.py, app.js prioritized)
        2. Path depth (files closer to root prioritized)
        3. Complexity (functions, classes, imports count)
        4. File size

        Args:
            max_files: Maximum number of files to sample
            skip_analyzed: Skip previously analyzed files (for incremental analysis)

        Returns:
            List of code samples with file paths, sorted by importance
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
                # Read file content (limit to 500 lines to avoid token limits)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[:500]
                    content = ''.join(lines)

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

            except Exception as e:
                logger.debug(f"Failed to read {file_path}: {e}")
                continue

        # Sort by score (descending) and take top N
        file_scores.sort(key=lambda x: x['score'], reverse=True)
        selected_files = file_scores[:max_files]

        logger.info(f"Selected {len(selected_files)} files from {len(file_scores)} candidates")
        if selected_files:
            logger.info(f"Top file: {selected_files[0]['path']} (score: {selected_files[0]['score']:.1f})")

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
        Build the prompt for Claude Code API.

        Args:
            code_samples: List of code samples to analyze

        Returns:
            Formatted prompt string
        """
        mode_name = self.mode_config['name']
        priorities = ', '.join(self.mode_config['priorities'])
        description = self.mode_config['description']

        # Build code context
        code_context = ""
        for sample in code_samples:
            code_context += f"\n\n### File: {sample['path']}\n```{sample['extension'][1:]}\n{sample['content'][:2000]}\n```"

        prompt = f"""당신은 전문 코드 리뷰어입니다. 다음 프로젝트를 "{mode_name}" 관점에서 분석해주세요.

**분석 우선순위**: {description}

**코드 샘플**:{code_context}

다음 항목을 중점적으로 분석하고, 우선순위별로 정리해주세요:

1. **Critical (치명적)**: 보안 취약점, 치명적 버그, 데이터 손실 위험
2. **Warning (경고)**: 성능 이슈, 코드 중복, 복잡도 초과, 나쁜 패턴
3. **Info (정보)**: 개선 제안, 리팩토링 방향, 코드 스타일

각 이슈에 대해 다음 형식으로 응답해주세요:

**[심각도] 이슈 제목**
- 파일: 파일경로 (있다면)
- 설명: 구체적인 문제 설명
- 제안: 개선 방안

총 10개 이내의 가장 중요한 이슈만 보고해주세요."""

        return prompt

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Claude's response into structured data.

        Args:
            response_text: Raw response from Claude

        Returns:
            Structured analysis results
        """
        issues = []
        current_severity = 'info'

        for line in response_text.split('\n'):
            line = line.strip()

            # Detect severity markers
            if line.startswith('**[Critical]') or line.startswith('**Critical'):
                current_severity = 'critical'
                title = line.replace('**[Critical]', '').replace('**Critical', '').replace('**', '').strip()
                if title:
                    issues.append({
                        'severity': 'critical',
                        'title': title,
                        'details': []
                    })
            elif line.startswith('**[Warning]') or line.startswith('**Warning'):
                current_severity = 'warning'
                title = line.replace('**[Warning]', '').replace('**Warning', '').replace('**', '').strip()
                if title:
                    issues.append({
                        'severity': 'warning',
                        'title': title,
                        'details': []
                    })
            elif line.startswith('**[Info]') or line.startswith('**Info'):
                current_severity = 'info'
                title = line.replace('**[Info]', '').replace('**Info', '').replace('**', '').strip()
                if title:
                    issues.append({
                        'severity': 'info',
                        'title': title,
                        'details': []
                    })
            elif line.startswith('-') and issues:
                # Add detail to the last issue
                issues[-1]['details'].append(line[1:].strip())

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
            logger.info(f"Starting AI analysis for {self.project_path} in {self.mode} mode")

            # Collect code samples (smart selection: 50 most important files)
            code_samples = self._collect_code_samples(max_files=50, skip_analyzed=True)

            if not code_samples:
                logger.warning(f"No code files found to analyze in {self.project_path}")
                return {
                    'mode': self.mode,
                    'error': 'No code files found to analyze',
                    'issues': [],
                    'summary': {'total_issues': 0, 'by_severity': {'critical': 0, 'warning': 0, 'info': 0}}
                }

            logger.info(f"Collected {len(code_samples)} code samples for AI analysis")

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
                timeout=60.0  # 60 second timeout
            )

            # Extract response text
            response_text = message.content[0].text
            logger.info("Successfully received AI analysis response")

            # Parse and return results
            result = self._parse_ai_response(response_text)
            logger.info(f"AI analysis found {result['summary']['total_issues']} issues")
            return result

        except anthropic.APIConnectionError as e:
            logger.error(f"Claude API connection error: {e}")
            return {
                'mode': self.mode,
                'error': f'Failed to connect to Claude API: {str(e)}. Check your internet connection.',
                'issues': [],
                'summary': {'total_issues': 0, 'by_severity': {'critical': 0, 'warning': 0, 'info': 0}}
            }
        except anthropic.RateLimitError as e:
            logger.error(f"Claude API rate limit exceeded: {e}")
            return {
                'mode': self.mode,
                'error': f'API rate limit exceeded: {str(e)}. Please try again later.',
                'issues': [],
                'summary': {'total_issues': 0, 'by_severity': {'critical': 0, 'warning': 0, 'info': 0}}
            }
        except anthropic.AuthenticationError as e:
            logger.error(f"Claude API authentication error: {e}")
            return {
                'mode': self.mode,
                'error': f'Authentication failed: {str(e)}. Check your ANTHROPIC_API_KEY.',
                'issues': [],
                'summary': {'total_issues': 0, 'by_severity': {'critical': 0, 'warning': 0, 'info': 0}}
            }
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}", exc_info=True)
            return {
                'mode': self.mode,
                'error': f'Claude API error: {str(e)}',
                'issues': [],
                'summary': {'total_issues': 0, 'by_severity': {'critical': 0, 'warning': 0, 'info': 0}}
            }
        except Exception as e:
            logger.error(f"Unexpected error during AI analysis: {e}", exc_info=True)
            return {
                'mode': self.mode,
                'error': f'AI analysis failed: {str(e)}',
                'issues': [],
                'summary': {'total_issues': 0, 'by_severity': {'critical': 0, 'warning': 0, 'info': 0}}
            }

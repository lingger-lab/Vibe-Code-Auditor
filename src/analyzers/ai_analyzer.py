"""AI-powered code analysis using Claude Code API."""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
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

    def _collect_code_samples(self, max_files: int = 10) -> List[Dict[str, str]]:
        """
        Collect representative code samples from the project.

        Args:
            max_files: Maximum number of files to sample

        Returns:
            List of code samples with file paths
        """
        code_samples = []
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

        count = 0
        for file_path in self.project_path.rglob('*'):
            if count >= max_files:
                break

            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue

            # Only include relevant code files
            if file_path.is_file() and file_path.suffix in file_extensions:
                try:
                    # Read file content (limit to 500 lines to avoid token limits)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()[:500]
                        content = ''.join(lines)

                    if content.strip():  # Only include non-empty files
                        relative_path = file_path.relative_to(self.project_path)
                        code_samples.append({
                            'path': str(relative_path),
                            'content': content,
                            'extension': file_path.suffix
                        })
                        count += 1

                except Exception:
                    continue  # Skip files that can't be read

        return code_samples

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

            # Collect code samples
            code_samples = self._collect_code_samples(max_files=10)

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

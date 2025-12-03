"""Tests for ai_analyzer module with mocked API calls."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import anthropic

from src.analyzers.ai_analyzer import AIAnalyzer, DEFAULT_CLAUDE_TIMEOUT


@pytest.mark.unit
class TestAIAnalyzer:
    """Test cases for AIAnalyzer class with mocked API."""

    def test_init(self, sample_project):
        """Test AIAnalyzer initialization."""
        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic'):
            analyzer = AIAnalyzer(sample_project, 'deployment')

            assert analyzer.project_path == sample_project
            assert analyzer.mode == 'deployment'
            assert analyzer.mode_config is not None

    def test_collect_code_samples(self, sample_project):
        """Test collecting code samples from project."""
        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic'):
            analyzer = AIAnalyzer(sample_project, 'deployment')
            samples = analyzer._collect_code_samples(max_files=10)

            assert isinstance(samples, list)
            assert len(samples) > 0

            # Check sample structure
            for sample in samples:
                assert 'path' in sample
                assert 'content' in sample
                assert 'extension' in sample

    def test_collect_code_samples_limit(self, sample_project):
        """Test code sample collection respects max_files limit."""
        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic'):
            analyzer = AIAnalyzer(sample_project, 'deployment')
            samples = analyzer._collect_code_samples(max_files=2)

            assert len(samples) <= 2

    def test_collect_code_samples_empty_project(self, temp_project_dir):
        """Test collecting code samples from empty project."""
        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic'):
            analyzer = AIAnalyzer(temp_project_dir, 'deployment')
            samples = analyzer._collect_code_samples()

            assert samples == []

    def test_build_analysis_prompt(self, sample_project):
        """Test building analysis prompt."""
        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic'):
            analyzer = AIAnalyzer(sample_project, 'deployment')
            code_samples = [
                {
                    'path': 'test.py',
                    'content': 'def test(): pass',
                    'extension': '.py'
                }
            ]

            prompt = analyzer._build_analysis_prompt(code_samples)

            assert isinstance(prompt, str)
            assert 'deployment' in prompt.lower() or '배포' in prompt
            assert 'test.py' in prompt
            assert 'Critical' in prompt
            assert 'Warning' in prompt
            assert 'Info' in prompt

    def test_parse_ai_response_with_issues(self, sample_project):
        """Test parsing AI response with issues."""
        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic'):
            analyzer = AIAnalyzer(sample_project, 'deployment')

            response_text = """
**[Critical] SQL Injection Vulnerability**
- 파일: auth.py
- 설명: SQL 쿼리에 사용자 입력이 직접 사용됨
- 제안: Prepared statements 사용

**[Warning] Code Duplication**
- 설명: 중복 코드 발견
- 제안: 공통 함수로 리팩토링

**[Info] Improve Naming**
- 설명: 변수명 개선 필요
"""

            result = analyzer._parse_ai_response(response_text)

            assert result['mode'] == 'deployment'
            assert 'raw_response' in result

            issues = result['issues']
            # 최소 3개 이상의 이슈가 있어야 한다 (파서가 세부 이슈를 더 만들 수 있음)
            assert len(issues) >= 3

            titles = [i.get('title') for i in issues]
            severities = [i.get('severity') for i in issues]

            # 핵심 이슈들이 포함되어 있는지 확인
            assert "SQL Injection Vulnerability" in titles
            assert "Code Duplication" in titles
            assert "Improve Naming" in titles

            # 세 가지 심각도 타입이 모두 존재하는지 확인
            for expected in ("critical", "warning", "info"):
                assert expected in severities

    def test_parse_ai_response_empty(self, sample_project):
        """Test parsing empty AI response."""
        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic'):
            analyzer = AIAnalyzer(sample_project, 'deployment')

            result = analyzer._parse_ai_response("")

            assert result['issues'] == []
            assert result['summary']['total_issues'] == 0

    def test_analyze_success(self, sample_project):
        """Test successful AI analysis with mocked API."""
        # Mock the Anthropic client
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_content = MagicMock()
        mock_content.text = """
**[Critical] Security Issue**
- 파일: test.py
- 설명: 보안 취약점 발견
"""
        mock_message.content = [mock_content]
        mock_client.messages.create.return_value = mock_message

        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic', return_value=mock_client):
            analyzer = AIAnalyzer(sample_project, 'deployment')
            result = analyzer.analyze()

            assert result['mode'] == 'deployment'
            assert 'issues' in result
            assert result['summary']['total_issues'] > 0
            assert 'error' not in result

            # Verify API was called
            mock_client.messages.create.assert_called_once()

    def test_analyze_no_code_files(self, temp_project_dir):
        """Test analysis with no code files."""
        mock_client = MagicMock()

        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic', return_value=mock_client):
            analyzer = AIAnalyzer(temp_project_dir, 'deployment')
            result = analyzer.analyze()

            assert result['error'] == 'No code files found to analyze'
            assert result['summary']['total_issues'] == 0

            # API should not be called
            mock_client.messages.create.assert_not_called()

    def test_analyze_api_connection_error(self, sample_project):
        """Test analysis with API connection error."""
        mock_client = MagicMock()
        # Create a mock request object
        mock_request = MagicMock()
        mock_request.url = "https://api.anthropic.com/v1/messages"
        mock_client.messages.create.side_effect = anthropic.APIConnectionError(
            message="Connection failed",
            request=mock_request
        )

        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic', return_value=mock_client):
            analyzer = AIAnalyzer(sample_project, 'deployment')
            result = analyzer.analyze()

            assert 'error' in result
            assert 'Failed to connect' in result['error']
            assert result['summary']['total_issues'] == 0

    def test_analyze_rate_limit_error(self, sample_project):
        """Test analysis with rate limit error."""
        mock_client = MagicMock()
        # Create mock response object
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_client.messages.create.side_effect = anthropic.RateLimitError(
            "Rate limit exceeded",
            response=mock_response,
            body={"error": {"message": "Rate limit exceeded"}}
        )

        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic', return_value=mock_client):
            analyzer = AIAnalyzer(sample_project, 'deployment')
            result = analyzer.analyze()

            assert 'error' in result
            assert 'rate limit' in result['error'].lower()
            assert result['summary']['total_issues'] == 0

    def test_analyze_authentication_error(self, sample_project):
        """Test analysis with authentication error."""
        mock_client = MagicMock()
        # Create mock response object
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_client.messages.create.side_effect = anthropic.AuthenticationError(
            "Invalid API key",
            response=mock_response,
            body={"error": {"message": "Invalid API key"}}
        )

        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic', return_value=mock_client):
            analyzer = AIAnalyzer(sample_project, 'deployment')
            result = analyzer.analyze()

            assert 'error' in result
            assert 'Authentication failed' in result['error']
            assert result['summary']['total_issues'] == 0

    def test_analyze_generic_api_error(self, sample_project):
        """Test analysis with generic API error."""
        mock_client = MagicMock()
        # Create mock request object
        mock_request = MagicMock()
        mock_request.url = "https://api.anthropic.com/v1/messages"
        mock_client.messages.create.side_effect = anthropic.APIError(
            "Generic error",
            request=mock_request,
            body={"error": {"message": "Generic error"}}
        )

        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic', return_value=mock_client):
            analyzer = AIAnalyzer(sample_project, 'deployment')
            result = analyzer.analyze()

            assert 'error' in result
            assert 'Claude API error' in result['error']
            assert result['summary']['total_issues'] == 0

    def test_analyze_unexpected_error(self, sample_project):
        """Test analysis with unexpected error."""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = ValueError("Unexpected error")

        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic', return_value=mock_client):
            analyzer = AIAnalyzer(sample_project, 'deployment')
            result = analyzer.analyze()

            assert 'error' in result
            assert 'AI analysis failed' in result['error']
            assert result['summary']['total_issues'] == 0

    def test_analyze_personal_mode(self, sample_project):
        """Test analysis in personal mode."""
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "**[Info] Code style improvement**\n- 설명: 코드 스타일 개선"
        mock_message.content = [mock_content]
        mock_client.messages.create.return_value = mock_message

        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic', return_value=mock_client):
            analyzer = AIAnalyzer(sample_project, 'personal')
            result = analyzer.analyze()

            assert result['mode'] == 'personal'
            assert 'issues' in result

    def test_code_sample_file_reading_error(self, temp_project_dir):
        """Test handling of file reading errors during code collection."""
        # Create a file that might cause reading issues
        unreadable_file = temp_project_dir / 'test.py'
        unreadable_file.write_text('test content')

        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic'):
            analyzer = AIAnalyzer(temp_project_dir, 'deployment')

            # Mock open to raise exception
            with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'test')):
                samples = analyzer._collect_code_samples()

                # Should handle error gracefully
                assert isinstance(samples, list)

    def test_parse_response_alternate_formats(self, sample_project):
        """Test parsing AI response with alternate formatting."""
        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic'):
            analyzer = AIAnalyzer(sample_project, 'deployment')

            # Test with alternate severity format (without brackets)
            response_text = """
**Critical Security Issue**
- 설명: 보안 문제

**Warning Performance Issue**
- 설명: 성능 문제

**Info Code Style**
- 설명: 스타일 개선
"""

            result = analyzer._parse_ai_response(response_text)

            # Should still detect issues
            assert len(result['issues']) >= 1

    def test_collect_code_samples_excludes_dirs(self, temp_project_dir):
        """Test that code collection excludes specified directories."""
        # Create files in excluded directories
        node_modules = temp_project_dir / 'node_modules'
        node_modules.mkdir()
        (node_modules / 'test.js').write_text('console.log("test");')

        venv = temp_project_dir / 'venv'
        venv.mkdir()
        (venv / 'test.py').write_text('print("test")')

        # Create file in included directory
        (temp_project_dir / 'main.py').write_text('print("main")')

        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic'):
            analyzer = AIAnalyzer(temp_project_dir, 'deployment')
            samples = analyzer._collect_code_samples()

            # Should only collect main.py, not files from excluded dirs
            paths = [s['path'] for s in samples]
            assert 'main.py' in paths
            assert not any('node_modules' in p for p in paths)
            assert not any('venv' in p for p in paths)

    def test_collect_code_samples_file_extensions(self, temp_project_dir):
        """Test that code collection only includes specific file extensions."""
        # Create files with various extensions
        (temp_project_dir / 'code.py').write_text('print("python")')
        (temp_project_dir / 'code.js').write_text('console.log("js")')
        (temp_project_dir / 'data.json').write_text('{"key": "value"}')
        (temp_project_dir / 'readme.txt').write_text('readme')

        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic'):
            analyzer = AIAnalyzer(temp_project_dir, 'deployment')
            samples = analyzer._collect_code_samples()

            # Should only include code files (.py, .js, etc), not .json or .txt
            extensions = [s['extension'] for s in samples]
            assert '.py' in extensions
            assert '.js' in extensions
            assert '.json' not in extensions
            assert '.txt' not in extensions

    def test_collect_code_samples_line_limit(self, temp_project_dir):
        """Test that code samples are limited to 500 lines."""
        # Create a large file
        large_file = temp_project_dir / 'large.py'
        large_content = '\n'.join([f'# Line {i}' for i in range(1000)])
        large_file.write_text(large_content)

        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic'):
            analyzer = AIAnalyzer(temp_project_dir, 'deployment')
            samples = analyzer._collect_code_samples()

            # File content should be limited to 500 lines
            found = False
            for sample in samples:
                if sample['path'] == 'large.py':
                    found = True
                    # Count lines using splitlines() which is more accurate
                    line_count = len(sample['content'].splitlines())
                    # readlines()[:500] reads first 500 lines, so we expect exactly 500
                    assert line_count == 500, f"Expected 500 lines, got {line_count}"

            assert found, "large.py not found in samples"

    def test_api_timeout_parameter(self, sample_project):
        """Test that API calls include timeout parameter."""
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "**[Info] Test**\n- Test issue"
        mock_message.content = [mock_content]
        mock_client.messages.create.return_value = mock_message

        with patch('src.analyzers.ai_analyzer.anthropic.Anthropic', return_value=mock_client):
            analyzer = AIAnalyzer(sample_project, 'deployment')
            analyzer.analyze()

            # Verify timeout was passed
            call_kwargs = mock_client.messages.create.call_args[1]
            assert 'timeout' in call_kwargs
            assert call_kwargs['timeout'] == DEFAULT_CLAUDE_TIMEOUT

"""End-to-end tests for CLI module."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from src.cli.main import audit
from src.utils.history_tracker import HistoryTracker
from src.utils.cache_manager import CacheManager


@pytest.mark.integration
class TestCLI:
    """Test cases for CLI commands."""

    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(audit, ['--help'])

        assert result.exit_code == 0
        assert 'Vibe-Code Auditor' in result.output
        assert '--path' in result.output
        assert '--mode' in result.output

    def test_cli_missing_required_path(self):
        """Test CLI fails without required --path argument."""
        runner = CliRunner()
        result = runner.invoke(audit, [])

        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'Error' in result.output

    def test_cli_init_config(self, sample_project):
        """Test --init-config flag creates template."""
        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--init-config'
        ])

        assert result.exit_code == 0
        assert '설정 파일 템플릿 생성됨' in result.output

        # Check template was created
        template_file = sample_project / '.vibe-auditor.yml.example'
        assert template_file.exists()

    def test_cli_show_history_no_data(self, sample_project):
        """Test --show-history with no existing history."""
        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--show-history'
        ])

        assert result.exit_code == 0
        assert '아직 분석 히스토리가 없습니다' in result.output

    def test_cli_show_history_with_data(self, sample_project, mock_analysis_results):
        """Test --show-history with existing history."""
        # Create some history
        tracker = HistoryTracker(sample_project)
        tracker.save_result('deployment', mock_analysis_results, None)

        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--show-history'
        ])

        assert result.exit_code == 0
        assert '분석 히스토리' in result.output
        assert '총 분석 횟수' in result.output

    def test_cli_clear_cache(self, sample_project):
        """Test --clear-cache flag."""
        # Create some cache
        cache_mgr = CacheManager(sample_project)
        cache_mgr.save_result('test_key', {'data': 'test'})

        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--clear-cache'
        ])

        assert result.exit_code == 0
        assert '캐시 데이터가 삭제되었습니다' in result.output

        # Verify cache was cleared
        assert cache_mgr.get_cached_result('test_key') is None

    def test_cli_analysis_skip_ai(self, sample_project):
        """Test running analysis with --skip-ai flag."""
        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--mode', 'deployment',
            '--skip-ai'
        ])

        assert result.exit_code == 0
        assert '프로젝트 언어 감지 중' in result.output
        assert '정적 분석 실행 중' in result.output
        assert 'AI 분석 건너뜀' in result.output
        assert '분석 완료' in result.output

    def test_cli_verbose_mode(self, sample_project):
        """Test CLI with --verbose flag."""
        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--skip-ai',
            '--verbose'
        ])

        # Verbose mode should complete successfully
        assert result.exit_code == 0

    def test_cli_quiet_mode(self, sample_project):
        """Test CLI with --quiet flag."""
        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--skip-ai',
            '--quiet'
        ])

        # Quiet mode should complete successfully
        assert result.exit_code == 0

    def test_cli_json_output(self, sample_project, tmp_path):
        """Test CLI with JSON output."""
        output_file = tmp_path / 'report.json'

        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--skip-ai',
            '--output', str(output_file),
            '--format', 'json'
        ])

        assert result.exit_code == 0
        assert output_file.exists()
        assert 'JSON 리포트 저장됨' in result.output

    def test_cli_html_output(self, sample_project, tmp_path):
        """Test CLI with HTML output."""
        output_file = tmp_path / 'report.html'

        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--skip-ai',
            '--output', str(output_file),
            '--format', 'html'
        ])

        assert result.exit_code == 0
        assert output_file.exists()
        assert 'HTML 리포트 저장됨' in result.output

    def test_cli_output_format_inference(self, sample_project, tmp_path):
        """Test CLI infers format from file extension."""
        output_file = tmp_path / 'report.json'

        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--skip-ai',
            '--output', str(output_file)
            # No --format specified, should infer from .json extension
        ])

        assert result.exit_code == 0
        assert output_file.exists()

    def test_cli_invalid_output_format(self, sample_project, tmp_path):
        """Test CLI with invalid output format."""
        output_file = tmp_path / 'report.xml'

        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--skip-ai',
            '--output', str(output_file)
        ])

        assert result.exit_code != 0
        assert '지원하지 않는 파일 형식' in result.output

    def test_cli_no_history_flag(self, sample_project):
        """Test --no-history flag prevents history tracking."""
        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--skip-ai',
            '--no-history'
        ])

        assert result.exit_code == 0

        # Check that no history was saved
        tracker = HistoryTracker(sample_project)
        history = tracker.get_history()
        assert len(history) == 0

    def test_cli_no_cache_flag(self, sample_project):
        """Test --no-cache flag bypasses cache."""
        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--skip-ai',
            '--no-cache'
        ])

        assert result.exit_code == 0

    def test_cli_with_config_file(self, sample_project):
        """Test CLI loads configuration from file."""
        # Create config file
        config_file = sample_project / '.vibe-auditor.yml'
        config_file.write_text("""
analysis:
  mode: personal
  skip_ai: true
""")

        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project)
        ])

        assert result.exit_code == 0
        assert '분석 완료' in result.output

    def test_cli_custom_config_file(self, sample_project, tmp_path):
        """Test CLI with custom config file path."""
        # Create custom config
        custom_config = tmp_path / 'custom.yml'
        custom_config.write_text("""
analysis:
  mode: deployment
  skip_ai: true
""")

        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--config', str(custom_config)
        ])

        assert result.exit_code == 0

    def test_cli_invalid_config_file(self, sample_project, tmp_path):
        """Test CLI with invalid config file."""
        # Create invalid config
        invalid_config = tmp_path / 'invalid.yml'
        invalid_config.write_text("invalid: yaml: syntax:")

        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--config', str(invalid_config)
        ])

        # Should handle gracefully
        assert result.exit_code != 0

    def test_cli_empty_project(self, temp_project_dir):
        """Test CLI with empty project (no code files)."""
        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(temp_project_dir),
            '--skip-ai'
        ])

        assert result.exit_code != 0
        assert '분석 가능한 코드 파일을 찾을 수 없습니다' in result.output

    def test_cli_mode_override(self, sample_project):
        """Test CLI mode argument overrides config file."""
        # Create config with personal mode
        config_file = sample_project / '.vibe-auditor.yml'
        config_file.write_text("analysis:\n  mode: personal")

        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--mode', 'deployment',  # Override to deployment
            '--skip-ai'
        ])

        assert result.exit_code == 0
        # Should use deployment mode
        assert '배포 관점' in result.output or 'deployment' in result.output.lower()

    def test_cli_creates_history_by_default(self, sample_project):
        """Test that CLI creates history by default."""
        runner = CliRunner()
        result = runner.invoke(audit, [
            '--path', str(sample_project),
            '--skip-ai'
        ])

        assert result.exit_code == 0

        # Check history was created
        tracker = HistoryTracker(sample_project)
        history = tracker.get_history()
        assert len(history) > 0

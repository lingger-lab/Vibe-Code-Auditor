"""Integration tests for Vibe-Code Auditor."""

import pytest
from pathlib import Path
from src.detectors.language_detector import LanguageDetector
from src.analyzers.static_analyzer import StaticAnalyzer
from src.reporters.json_reporter import JSONReporter
from src.reporters.html_reporter import HTMLReporter
from src.utils.history_tracker import HistoryTracker
from src.utils.cache_manager import CacheManager


@pytest.mark.integration
class TestIntegrationWorkflow:
    """Integration tests for complete analysis workflow."""

    def test_full_analysis_workflow(self, sample_project):
        """Test complete analysis workflow from detection to reporting."""
        # Step 1: Detect languages
        detector = LanguageDetector(sample_project)
        languages = detector.detect()

        assert len(languages) > 0
        assert 'python' in languages

        # Step 2: Run static analysis
        analyzer = StaticAnalyzer(sample_project, languages, 'deployment', use_cache=False)
        static_results = analyzer.analyze()

        assert 'mode' in static_results
        assert 'languages' in static_results
        assert 'issues' in static_results
        assert 'summary' in static_results

        # Step 3: Generate JSON report
        json_reporter = JSONReporter('deployment')
        json_report = json_reporter.generate_report(
            static_results,
            None,
            sample_project,
            None
        )

        assert 'metadata' in json_report
        assert 'summary' in json_report
        assert 'static_analysis' in json_report

        # Step 4: Save to history
        tracker = HistoryTracker(sample_project)
        tracker.save_result('deployment', static_results, None)

        history = tracker.get_history()
        assert len(history) > 0

    def test_caching_workflow(self, sample_project):
        """Test analysis caching workflow."""
        # First run - should create cache
        analyzer1 = StaticAnalyzer(sample_project, ['python'], 'deployment', use_cache=True)
        results1 = analyzer1.analyze()

        # Second run - should use cache
        analyzer2 = StaticAnalyzer(sample_project, ['python'], 'deployment', use_cache=True)
        results2 = analyzer2.analyze()

        # Results should be identical (from cache)
        assert results1['summary'] == results2['summary']

    def test_report_generation_all_formats(self, sample_project, mock_analysis_results):
        """Test generating reports in all formats."""
        # JSON report
        json_reporter = JSONReporter('deployment')
        json_output = sample_project / 'report.json'
        json_reporter.generate_report(mock_analysis_results, None, sample_project, json_output)

        assert json_output.exists()

        # HTML report
        html_reporter = HTMLReporter('deployment')
        html_output = sample_project / 'report.html'
        html_reporter.generate_report(mock_analysis_results, None, sample_project, html_output)

        assert html_output.exists()

    def test_history_tracking_over_time(self, sample_project, mock_analysis_results):
        """Test history tracking over multiple runs."""
        tracker = HistoryTracker(sample_project)

        # Simulate 3 analysis runs
        for i in range(3):
            # Modify issue count
            results = mock_analysis_results.copy()
            results['summary']['total_issues'] = 10 - i  # Improving trend

            tracker.save_result('deployment', results, None)

        # Check history
        history = tracker.get_history()
        assert len(history) == 3

        # Check trend
        trend = tracker.get_trend_data()
        assert trend['total_runs'] == 3
        assert trend['trend'] == 'improving'

    def test_cache_invalidation_on_file_change(self, sample_project):
        """Test cache invalidation when files change."""
        cache_mgr = CacheManager(sample_project)

        # Create cache entry
        test_file = sample_project / 'main.py'
        project_files = [test_file]

        cache_mgr.save_result('test', {'data': 'original'}, project_files)

        # Verify cache exists
        cached = cache_mgr.get_cached_result('test', project_files)
        assert cached is not None

        # Modify file
        current_content = test_file.read_text()
        test_file.write_text(current_content + "\n# Modified")

        # Cache should be invalidated
        cached_after = cache_mgr.get_cached_result('test', project_files)
        assert cached_after is None


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling in integration scenarios."""

    def test_analysis_with_no_files(self, temp_project_dir):
        """Test analysis behavior with empty project."""
        detector = LanguageDetector(temp_project_dir)
        languages = detector.detect()

        assert len(languages) == 0

    def test_cache_with_missing_directory(self, temp_project_dir):
        """Test cache manager with non-existent cache directory."""
        # Remove cache directory if it exists
        cache_dir = temp_project_dir / '.vibe-auditor-cache'
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)

        # Cache manager should create it
        cache_mgr = CacheManager(temp_project_dir)
        assert cache_mgr.cache_dir.exists()

    def test_history_with_no_data(self, temp_project_dir):
        """Test history tracker with no data."""
        tracker = HistoryTracker(temp_project_dir)

        trend = tracker.get_trend_data()

        assert trend['total_runs'] == 0
        assert trend['trend'] == 'no_data'

"""Tests for history_tracker module."""

import pytest
from pathlib import Path
from datetime import datetime
from src.utils.history_tracker import HistoryTracker


@pytest.mark.unit
class TestHistoryTracker:
    """Test cases for HistoryTracker class."""

    def test_init(self, temp_project_dir):
        """Test HistoryTracker initialization."""
        tracker = HistoryTracker(temp_project_dir)

        assert tracker.project_path == temp_project_dir
        assert tracker.history_dir == temp_project_dir / '.vibe-auditor-history'
        assert tracker.history_file == temp_project_dir / '.vibe-auditor-history' / 'history.json'

    def test_ensure_history_dir(self, temp_project_dir):
        """Test history directory creation."""
        tracker = HistoryTracker(temp_project_dir)

        assert tracker.history_dir.exists()
        assert tracker.history_dir.is_dir()

    def test_save_result(self, temp_project_dir, mock_analysis_results):
        """Test saving analysis result to history."""
        tracker = HistoryTracker(temp_project_dir)

        # Save result
        tracker.save_result('deployment', mock_analysis_results, None)

        # Load history
        history = tracker.get_history()

        assert len(history) == 1
        assert history[0]['mode'] == 'deployment'
        assert history[0]['summary']['total_issues'] == 2

    def test_save_multiple_results(self, temp_project_dir, mock_analysis_results):
        """Test saving multiple analysis results."""
        tracker = HistoryTracker(temp_project_dir)

        # Save multiple results
        tracker.save_result('deployment', mock_analysis_results, None)
        tracker.save_result('personal', mock_analysis_results, None)

        history = tracker.get_history()

        assert len(history) == 2

    def test_get_history_with_limit(self, temp_project_dir, mock_analysis_results):
        """Test getting history with limit."""
        tracker = HistoryTracker(temp_project_dir)

        # Save 5 results
        for _ in range(5):
            tracker.save_result('deployment', mock_analysis_results, None)

        # Get only 3 most recent
        history = tracker.get_history(limit=3)

        assert len(history) == 3

    def test_get_trend_data_no_history(self, temp_project_dir):
        """Test trend data when no history exists."""
        tracker = HistoryTracker(temp_project_dir)

        trend = tracker.get_trend_data()

        assert trend['total_runs'] == 0
        assert trend['trend'] == 'no_data'

    def test_get_trend_data_improving(self, temp_project_dir, mock_analysis_results):
        """Test trend detection for improving code quality."""
        tracker = HistoryTracker(temp_project_dir)

        # First run with more issues
        first_results = mock_analysis_results.copy()
        first_results['summary']['total_issues'] = 10

        tracker.save_result('deployment', first_results, None)

        # Second run with fewer issues
        second_results = mock_analysis_results.copy()
        second_results['summary']['total_issues'] = 5

        tracker.save_result('deployment', second_results, None)

        trend = tracker.get_trend_data()

        assert trend['total_runs'] == 2
        assert trend['trend'] == 'improving'
        assert trend['change'] == -5
        assert trend['change_percent'] == -50.0

    def test_get_trend_data_declining(self, temp_project_dir, mock_analysis_results):
        """Test trend detection for declining code quality."""
        tracker = HistoryTracker(temp_project_dir)

        # First run with fewer issues
        first_results = mock_analysis_results.copy()
        first_results['summary']['total_issues'] = 5

        tracker.save_result('deployment', first_results, None)

        # Second run with more issues
        second_results = mock_analysis_results.copy()
        second_results['summary']['total_issues'] = 10

        tracker.save_result('deployment', second_results, None)

        trend = tracker.get_trend_data()

        assert trend['total_runs'] == 2
        assert trend['trend'] == 'declining'
        assert trend['change'] == 5

    def test_get_trend_data_stable(self, temp_project_dir, mock_analysis_results):
        """Test trend detection for stable code quality."""
        tracker = HistoryTracker(temp_project_dir)

        # Save two runs with same issue count
        tracker.save_result('deployment', mock_analysis_results, None)
        tracker.save_result('deployment', mock_analysis_results, None)

        trend = tracker.get_trend_data()

        assert trend['total_runs'] == 2
        assert trend['trend'] == 'stable'
        assert trend['change'] == 0

    def test_clear_history(self, temp_project_dir, mock_analysis_results):
        """Test clearing history."""
        tracker = HistoryTracker(temp_project_dir)

        # Save some history
        tracker.save_result('deployment', mock_analysis_results, None)

        # Clear history
        tracker.clear_history()

        # History file should be deleted
        assert not tracker.history_file.exists()

    def test_export_history(self, temp_project_dir, mock_analysis_results):
        """Test exporting history."""
        tracker = HistoryTracker(temp_project_dir)

        # Save some history
        tracker.save_result('deployment', mock_analysis_results, None)

        # Export
        export_path = temp_project_dir / 'export.json'
        tracker.export_history(export_path)

        assert export_path.exists()

        # Verify export content
        import json
        with open(export_path, 'r') as f:
            export_data = json.load(f)

        assert 'project_path' in export_data
        assert 'total_runs' in export_data
        assert 'trend' in export_data
        assert 'history' in export_data

    def test_aggregate_severity(self, temp_project_dir, mock_analysis_results, mock_ai_results):
        """Test severity aggregation from static and AI results."""
        tracker = HistoryTracker(temp_project_dir)

        aggregated = tracker._aggregate_severity(mock_analysis_results, mock_ai_results)

        # mock_analysis_results has 1 warning, 1 info
        # mock_ai_results has 1 critical
        assert aggregated['critical'] == 1
        assert aggregated['warning'] == 1
        assert aggregated['info'] == 1

    def test_timeline_in_trend_data(self, temp_project_dir, mock_analysis_results):
        """Test timeline data in trend analysis."""
        tracker = HistoryTracker(temp_project_dir)

        # Save multiple results
        for i in range(3):
            tracker.save_result('deployment', mock_analysis_results, None)

        trend = tracker.get_trend_data()

        assert 'timeline' in trend
        assert len(trend['timeline']) == 3
        assert all('timestamp' in entry for entry in trend['timeline'])
        assert all('total_issues' in entry for entry in trend['timeline'])

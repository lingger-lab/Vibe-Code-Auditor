"""Tests for language_detector module."""

import pytest
from pathlib import Path
from src.detectors.language_detector import LanguageDetector


@pytest.mark.unit
class TestLanguageDetector:
    """Test cases for LanguageDetector class."""

    def test_init(self, temp_project_dir):
        """Test LanguageDetector initialization."""
        detector = LanguageDetector(temp_project_dir)

        assert detector.project_path == temp_project_dir
        assert detector.use_parallel is True
        assert detector.max_workers > 0

    def test_detect_python(self, sample_project):
        """Test detecting Python language."""
        detector = LanguageDetector(sample_project)

        languages = detector.detect()

        assert 'python' in languages

    def test_get_file_count(self, sample_project):
        """Test getting file count for a language."""
        detector = LanguageDetector(sample_project)

        python_count = detector.get_file_count('python')

        # sample_project has at least 4 Python files
        assert python_count >= 4

    def test_get_project_summary(self, sample_project):
        """Test getting project summary."""
        detector = LanguageDetector(sample_project)

        summary = detector.get_project_summary()

        assert 'languages' in summary
        assert 'primary_language' in summary
        assert 'file_counts' in summary

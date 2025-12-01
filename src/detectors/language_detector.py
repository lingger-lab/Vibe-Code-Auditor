"""Language detection module for identifying programming languages in a project."""

from pathlib import Path
from typing import List, Set
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from src.config.settings import LANGUAGE_PATTERNS, DEFAULT_EXCLUDE_PATTERNS
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class LanguageDetector:
    """Detects programming languages used in a project directory."""

    def __init__(self, project_path: Path, use_parallel: bool = True):
        """
        Initialize the language detector.

        Args:
            project_path: Path to the project directory to analyze
            use_parallel: Whether to use parallel processing for file scanning
        """
        self.project_path = project_path
        self.exclude_patterns = DEFAULT_EXCLUDE_PATTERNS
        self.use_parallel = use_parallel
        self.max_workers = min(32, (os.cpu_count() or 1) * 2)

    def _should_exclude(self, path: Path) -> bool:
        """
        Check if a path should be excluded from analysis.

        Args:
            path: Path to check

        Returns:
            True if path should be excluded, False otherwise
        """
        path_str = str(path)
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return True
        return False

    def _scan_directory(self, directory: Path) -> List[Path]:
        """
        Scan a single directory for code files.

        Args:
            directory: Directory to scan

        Returns:
            List of code file paths in this directory
        """
        code_files = []
        try:
            for item in directory.iterdir():
                if self._should_exclude(item):
                    continue

                if item.is_file():
                    code_files.append(item)
                elif item.is_dir():
                    # For parallel processing, we'll handle subdirectories separately
                    pass
        except PermissionError:
            logger.debug(f"Permission denied: {directory}")
        except Exception as e:
            logger.debug(f"Error scanning {directory}: {e}")

        return code_files

    def _scan_files(self) -> List[Path]:
        """
        Scan project directory for code files (with optional parallel processing).

        Returns:
            List of code file paths
        """
        if not self.use_parallel:
            # Sequential scanning (original method)
            code_files = []
            try:
                for file_path in self.project_path.rglob('*'):
                    if file_path.is_file() and not self._should_exclude(file_path):
                        code_files.append(file_path)
            except PermissionError:
                pass
            return code_files

        # Parallel scanning
        logger.debug(f"Scanning files with {self.max_workers} workers")
        code_files = []
        directories_to_scan = [self.project_path]
        scanned_dirs = set()

        # Collect all directories first
        try:
            for root_dir in self.project_path.rglob('*'):
                if root_dir.is_dir() and not self._should_exclude(root_dir):
                    directories_to_scan.append(root_dir)
        except PermissionError:
            pass

        # Scan directories in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_dir = {
                executor.submit(self._scan_directory, directory): directory
                for directory in directories_to_scan
            }

            for future in as_completed(future_to_dir):
                try:
                    files = future.result()
                    code_files.extend(files)
                except Exception as e:
                    directory = future_to_dir[future]
                    logger.debug(f"Error scanning directory {directory}: {e}")

        logger.debug(f"Found {len(code_files)} files")
        return code_files

    def detect(self) -> List[str]:
        """
        Detect programming languages used in the project.

        Returns:
            List of detected language names, sorted by prevalence
        """
        detected_languages: Set[str] = set()
        extension_counts = Counter()

        # Scan all files
        files = self._scan_files()

        for file_path in files:
            file_name = file_path.name
            file_ext = file_path.suffix

            # Check for language-specific files (e.g., package.json, requirements.txt)
            for lang, patterns in LANGUAGE_PATTERNS.items():
                if file_name in patterns['files']:
                    detected_languages.add(lang)

            # Check file extensions
            for lang, patterns in LANGUAGE_PATTERNS.items():
                if file_ext in patterns['extensions']:
                    detected_languages.add(lang)
                    extension_counts[lang] += 1

        # Sort languages by file count (most prevalent first)
        if extension_counts:
            sorted_languages = [
                lang for lang, _ in extension_counts.most_common()
            ]
            # Add languages detected by special files but not counted
            for lang in detected_languages:
                if lang not in sorted_languages:
                    sorted_languages.append(lang)
            return sorted_languages

        return list(detected_languages)

    def get_file_count(self, language: str) -> int:
        """
        Get the number of files for a specific language.

        Args:
            language: Language name

        Returns:
            Number of files for the language
        """
        if language not in LANGUAGE_PATTERNS:
            return 0

        count = 0
        files = self._scan_files()
        patterns = LANGUAGE_PATTERNS[language]

        for file_path in files:
            if file_path.suffix in patterns['extensions']:
                count += 1

        return count

    def get_project_summary(self) -> dict:
        """
        Get a summary of the project's language composition.

        Returns:
            Dictionary with language statistics
        """
        languages = self.detect()
        summary = {
            'languages': languages,
            'primary_language': languages[0] if languages else None,
            'file_counts': {}
        }

        for lang in languages:
            summary['file_counts'][lang] = self.get_file_count(lang)

        return summary
